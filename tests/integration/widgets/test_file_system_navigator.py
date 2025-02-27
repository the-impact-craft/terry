import contextlib
from pathlib import Path
from unittest.mock import patch

import pytest

from terry.domain.file_system.entities import ListDirOutput
from terry.presentation.cli.widgets.file_system_navigator import (
    FileSystemNavigator,
    PathListingContainer,
    FileSystemWidget,
    FileSystemNavigatorClasses,
)
from terry.presentation.cli.di_container import DiContainer
from terry.presentation.cli.screens.file_system_navigation.main import FileSystemNavigationModal
from tests.integration.utils import double_click, enter, click, focus

FOLDER_CLASS = FileSystemNavigatorClasses.DIRECTORY_LISTING_FOLDER.value
FILE_CLASS = FileSystemNavigatorClasses.DIRECTORY_LISTING_FILE.value

FILE_SYSTEM_WIDGET_CLASS_PATH = "terry.presentation.cli.widgets.file_system_navigator.FileSystemWidget"


class TestFileSystemNavigator:
    @pytest.mark.asyncio
    async def test_render(self, app, tmp_path, file_system_service):
        """
        Scenario: Rendering the file system navigator
            Given the file system navigator is initialized
            When the widget is rendered
            Then the FileSystemNavigator widget should be displayed
        """
        async with app.run_test() as pilot:
            async with self.navigator(pilot, tmp_path, file_system_service) as navigator:
                assert isinstance(navigator, FileSystemNavigator)

    @pytest.mark.asyncio
    async def test_mount_initial_path_listing_container(self, app, tmp_path, file_system_service):
        """
        Scenario: Mounting initial path listing container
            Given the file system navigator is initialized
            When the widget is mounted
            Then it should display the contents of the working directory
        """

        async with app.run_test() as pilot:
            async with self.navigator(pilot, tmp_path, file_system_service) as navigator:
                # Verify list_dir was called
                pilot.app.file_system_service.list_dir.assert_called_once()

                # Verify container was created
                container = navigator.query_one(PathListingContainer)
                assert container is not None

                # Verify widgets were created
                widgets = container.query(FileSystemWidget)
                assert len(widgets) == 2  # 1 folder + 1 file

    @pytest.mark.asyncio
    async def test_mount_empty_directory(self, app, tmp_path, file_system_service):
        """
        Scenario: Mounting empty directory
            Given the directory is empty
            When the widget is mounted
            Then no path listing container should be created
        """
        async with app.run_test() as pilot:
            pilot.app.file_system_service.list_dir.return_value = ListDirOutput(directories=[], files=[])
            async with self.navigator(pilot, tmp_path, file_system_service) as navigator:
                containers = navigator.query(PathListingContainer)
                assert len(containers) == 0

    @pytest.mark.asyncio
    async def test_folder_enter_navigation(self, app, tmp_path, file_system_service):
        """
        Scenario: Navigating to subfolder
            Given the file system navigator is mounted
            When I select a folder and press enter
            Then a new path listing container should be created for that folder
        """
        # Setup initial directory

        folder_path = tmp_path / Path("folder1")
        folder_path.mkdir()
        file_path = folder_path / Path("file1.txt")

        async with app.run_test() as pilot:
            pilot.app.file_system_service.list_dir.side_effect = [
                ListDirOutput(directories=[folder_path], files=[]),
                ListDirOutput(directories=[], files=[file_path]),
            ]

            async with self.navigator(pilot, tmp_path, file_system_service) as navigator:
                # Get and click the folder widget
                folder_widget = navigator.query_one(f".{FOLDER_CLASS}")
                await enter(pilot, folder_widget)

                # Verify new container was created
                containers = list(navigator.query(PathListingContainer).results())
                assert len(containers) == 2  # Initial + new container

    @pytest.mark.asyncio
    async def test_folder_click_navigation(self, app, tmp_path, file_system_service):
        """
        Scenario: Navigating to subfolder
            Given the file system navigator is mounted
            When I click on a folder
            Then a new path listing container should be created for that folder
        """
        # Setup initial directory

        folder_path = tmp_path / Path("folder1")
        folder_path.mkdir()
        file_path = folder_path / Path("file1.txt")
        side_effect = [
            ListDirOutput(directories=[folder_path], files=[]),
            ListDirOutput(directories=[], files=[file_path]),
        ]

        async with app.run_test() as pilot:
            pilot.app.file_system_service.list_dir.side_effect = side_effect

            async with self.navigator(pilot, tmp_path, file_system_service) as navigator:
                # Get and click the folder widget
                folder_widget = navigator.query_one(f".{FOLDER_CLASS}")
                await click(pilot, folder_widget)

                # Verify new container was created
                containers = list(navigator.query(PathListingContainer).results())
                assert len(containers) == 2  # Initial + new container

    @pytest.mark.asyncio
    async def test_back_folder_click(self, app, tmp_path, file_system_service):
        """
        Scenario: Navigating to initial folder
            Given the file system navigator is mounted
            When I click on the back folder button
            Then the initial path listing container should be displayed
        """
        # Setup initial directory

        folder_path1 = tmp_path / Path("folder1")
        folder_path2 = tmp_path / Path("folder1/folder2")
        folder_path3 = tmp_path / Path("folder1/folder2/folder3")

        for folder in [folder_path1, folder_path2, folder_path3]:
            folder.mkdir()

        side_effect = [
            ListDirOutput(directories=[folder_path1], files=[]),
            ListDirOutput(directories=[folder_path2], files=[]),
            ListDirOutput(directories=[folder_path3], files=[]),
            ListDirOutput(directories=[folder_path1], files=[]),
        ]

        async with app.run_test() as pilot:
            pilot.app.file_system_service.list_dir.side_effect = side_effect

            async with self.navigator(pilot, tmp_path, file_system_service) as navigator:
                containers = list(navigator.query(PathListingContainer))
                assert len(containers) == 1

                for i in range(2):
                    containers = list(navigator.query(PathListingContainer))
                    assert len(containers) == i + 1

                    widgets = containers[-1].query(FileSystemWidget)
                    await enter(pilot, widgets[0])
                    await pilot.press("right")
                    await pilot.pause()

                containers = list(navigator.query(PathListingContainer))
                assert len(containers) == 3

                widgets = containers[0].query(FileSystemWidget)

                await enter(pilot, widgets[0])
                await pilot.pause()

    @pytest.mark.asyncio
    async def test_keyboard_navigation(self, app, tmp_path, file_system_service):
        """
        Scenario: Keyboard navigation
            Given the file system navigator is mounted
            When I use keyboard arrows
            Then the focus should move accordingly
        """
        folders = [tmp_path / Path("folder1"), tmp_path / Path("folder2"), tmp_path / Path("folder1/folder3")]
        for folder in folders:
            folder.mkdir()

        side_effect = [
            ListDirOutput(directories=folders[:-1], files=[]),
            ListDirOutput(directories=[folders[-1]], files=[]),
        ]

        async with app.run_test() as pilot:
            pilot.app.file_system_service.list_dir.side_effect = side_effect

            async with self.navigator(pilot, tmp_path, file_system_service) as navigator:
                await pilot.pause()

                containers_number = len(list(navigator.query(PathListingContainer)))
                assert containers_number == 1
                left_container = navigator.query_one(PathListingContainer)
                widgets = left_container.query(FileSystemWidget)

                # Initial focus should be on first widget
                widgets[0].focus()
                await pilot.pause()
                assert widgets[0].has_focus

                # Test down navigation
                await pilot.press("down")
                await pilot.pause()
                assert widgets[1].has_focus

                # Test up navigation
                await pilot.press("up")
                await pilot.pause()
                assert widgets[0].has_focus

                # Click on folder to open inner folder tab
                await pilot.press("enter")
                await pilot.pause()

                containers = list(navigator.query(PathListingContainer))
                assert len(containers) == 2

                right_container = containers[-1]
                widgets = right_container.query(FileSystemWidget)
                await pilot.press("right")
                assert widgets[0].has_focus

                # Test left navigation
                await pilot.press("left")
                await pilot.pause()

                widgets = left_container.query(FileSystemWidget)
                assert widgets[0].has_focus

                # Test right navigation
                await pilot.press("right")
                await pilot.pause()

                widgets = right_container.query(FileSystemWidget)
                assert widgets[0].has_focus

    @pytest.mark.asyncio
    async def test_empty_folder(self, app, tmp_path, file_system_service):
        """
        Scenario: Empty folder
        Given the directory is empty
        When I click on the folder
        Then no path listing container should be created
        """
        folder = tmp_path / Path("folder1")
        folder.mkdir()

        side_effect = [ListDirOutput(directories=[folder], files=[]), ListDirOutput(directories=[], files=[])]

        async with app.run_test() as pilot:
            pilot.app.file_system_service.list_dir.side_effect = side_effect

            async with self.navigator(pilot, tmp_path, file_system_service) as navigator:
                await pilot.pause()

                containers_number = len(list(navigator.query(PathListingContainer)))
                assert containers_number == 1
                container = navigator.query_one(PathListingContainer)
                widgets = container.query(FileSystemWidget)

                # Initial focus should be on first widget
                await pilot.press("right")
                await pilot.pause()

                # Click on folder to open inner folder tab
                await enter(pilot, widgets[0])

                # Verify no new container was created
                containers = list(navigator.query(PathListingContainer))
                assert len(containers) == 1

    @pytest.mark.asyncio
    async def test_file_double_click(self, app, tmp_path, file_system_service):
        """
        Scenario: Double-clicking a file
            Given the file system navigator is mounted
            When I double-click a file
            Then an ActivePathFileDoubleClicked message should be posted
        """
        file = tmp_path / Path("file1.txt")
        file.touch()

        async with app.run_test() as pilot:
            pilot.app.file_system_service.list_dir.return_value = ListDirOutput(directories=[], files=[file])

            async with self.navigator(pilot, tmp_path, file_system_service) as navigator:
                file_widget = navigator.query_one(f".{FILE_CLASS}")
                with patch(f"{FILE_SYSTEM_WIDGET_CLASS_PATH}.send_event") as post_message_mock:
                    # Simulate double click
                    await double_click(pilot, file_widget)
                    # Verify message was posted
                    post_message_mock.assert_called_with(FileSystemWidget.FileDoubleClick)

    @pytest.mark.asyncio
    async def test_active_path_tracking(self, app, tmp_path, file_system_service):
        """
        Scenario: Active path tracking
            Given the file system navigator is mounted
            When I focus on a file or folder
            Then the active path should be updated
        """
        folder = tmp_path / Path("folder1")
        folder.mkdir()

        async with app.run_test() as pilot:
            pilot.app.file_system_service.list_dir.return_value = ListDirOutput(directories=[folder], files=[])

            async with self.navigator(pilot, tmp_path, file_system_service) as navigator:
                folder_widget = navigator.query_one(f".{FOLDER_CLASS}")

                # Simulate focus
                await focus(pilot, folder_widget)

                # Verify active path was updated
                assert navigator.active_path == folder

    @contextlib.asynccontextmanager
    async def navigator(self, pilot, tmp_path, file_system_service, callback=None):
        di_container = DiContainer()
        di_container.config.work_dir.from_value(tmp_path)
        di_container.wire(packages=["terry.presentation.cli", "tests"])

        with di_container.file_system_service.override(file_system_service):
            if not callback:
                await pilot.app.push_screen(FileSystemNavigationModal())
            else:
                await pilot.app.push_screen(FileSystemNavigationModal(), callback=callback)

            try:
                navigator = pilot.app.screen.query_one(FileSystemNavigator)
            except Exception:
                raise AssertionError("File system navigator not found in screen")

        yield navigator
