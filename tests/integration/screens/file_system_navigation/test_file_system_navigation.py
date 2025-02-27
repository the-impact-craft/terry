import contextlib
from unittest.mock import MagicMock

import pytest
from textual.widgets import Static

from terry.presentation.cli.widgets.file_system_navigator import FileSystemNavigator
from terry.presentation.cli.screens.file_system_navigation.main import (
    FileSystemNavigationModal,
)
from tests.integration.utils import click, DEFAULT_SCREEN_ID


class TestFileSystemNavigationModal:
    """
    Feature: File System Navigation Modal
        As a user
        I want to navigate and select files from the file system
        So that I can choose files for various operations
    """

    CONTROLS_ID = "#controls"
    CLOSE_BUTTON_ID = "#close"
    APPLY_BUTTON_ID = "#apply"
    HEADER_ID = "#header"
    PLAN_BUTTON_ID = "#plan"

    @pytest.mark.asyncio
    async def test_modal_initialization(self, app):
        """
        Scenario: Modal initialization
            Given I have a file system service
            And a working directory
            When I initialize the modal
            Then it should be properly configured
        """
        async with app.run_test() as pilot:
            async with self.file_system_navigation_modal(pilot):
                assert isinstance(pilot.app.screen, FileSystemNavigationModal)

    @pytest.mark.asyncio
    async def test_modal_initialization_failed(self, app, file_system_service, tmp_path):
        with pytest.raises(TypeError) as exc_info:
            FileSystemNavigationModal(file_system_service, "work_dir")
            assert "Invalid work_dir" in str(exc_info.value)

        with pytest.raises(TypeError) as exc_info:
            FileSystemNavigationModal(file_system_service, tmp_path, ["validation_rule"])
            assert "rule must be an instance of FileSystemSelectionValidationRule" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_compose_ui_elements(self, app):
        """
        Scenario: UI composition
            Given the modal is initialized
            When it composes its UI
            Then all required elements should be present
        """
        async with app.run_test() as pilot:
            async with self.file_system_navigation_modal(pilot) as modal:
                assert isinstance(pilot.app.screen, FileSystemNavigationModal)
                # Verify path label
                path_label = modal.query_one("#active-path", Static)
                assert path_label is not None
                assert path_label.renderable == ""

                # Verify file system navigator
                navigator = modal.query_one(FileSystemNavigator)
                assert navigator is not None

                # Verify control buttons
                controls = modal.query("#controls FileSystemViewControlLabel")
                assert len(controls) == 2
                assert "Close" in controls[0].renderable
                assert "Apply" in controls[1].renderable

    @pytest.mark.asyncio
    async def test_active_path_update(self, app, tmp_path):
        """
        Scenario: Active path update
            Given the modal is displayed
            When the active path changes in the navigator
            Then the path label should be updated
        """
        test_path = tmp_path / "test.tf"

        async with app.run_test() as pilot:
            async with self.file_system_navigation_modal(pilot) as modal:
                assert isinstance(pilot.app.screen, FileSystemNavigationModal)
                # Simulate path change event
                event = FileSystemNavigator.ActivePathChanged(test_path)
                modal.on_active_path_changed(event)

                await pilot.pause()

                # Verify path label update
                path_label = modal.query_one("#active-path", Static)
                assert path_label.renderable == "test.tf"
                assert modal.active_path == test_path

    @pytest.mark.asyncio
    async def test_file_double_click_with_validation(self, app, tmp_path):
        """
        Scenario: File double-click with validation
            Given the modal has validation rules
            When I double-click a file
            Then it should validate the file before selection
        """
        valid_path = tmp_path / "valid.tf"

        callback_mock = MagicMock()
        async with app.run_test() as pilot:
            async with self.file_system_navigation_modal(pilot, callback_mock) as modal:
                assert isinstance(pilot.app.screen, FileSystemNavigationModal)
                event = FileSystemNavigator.ActivePathFileDoubleClicked(valid_path)
                modal.on_path_double_clicked(event)

                await pilot.pause()
                assert pilot.app.screen.id == DEFAULT_SCREEN_ID
                callback_mock.assert_called_once_with(valid_path)

    @pytest.mark.asyncio
    async def test_close_action(self, app):
        """
        Scenario: Modal close action
            Given the modal is displayed
            When I click the close button
            Then the modal should be dismissed without selection
        """
        async with app.run_test() as pilot:
            async with self.file_system_navigation_modal(pilot):
                assert isinstance(pilot.app.screen, FileSystemNavigationModal)
                # Simulate close button click
                close_button = self._get_button_by_id(pilot, self.CLOSE_BUTTON_ID)
                await click(pilot, close_button)
                assert pilot.app.screen.id == DEFAULT_SCREEN_ID

    @pytest.mark.asyncio
    async def test_apply_action(self, app, tmp_path):
        """
        Scenario: Modal aaply action
            Given the modal is displayed
            When I click the apply button
            Then the modal should be dismissed without selection
        """
        callback_mock = MagicMock()
        test_path = tmp_path / "test.tf"
        async with app.run_test() as pilot:
            async with self.file_system_navigation_modal(pilot, callback_mock) as modal:
                assert isinstance(pilot.app.screen, FileSystemNavigationModal)
                event = FileSystemNavigator.ActivePathChanged(test_path)
                modal.on_active_path_changed(event)

                await pilot.pause()

                # Simulate apply button click
                apply_button = self._get_button_by_id(pilot, self.APPLY_BUTTON_ID)
                await click(pilot, apply_button)
                assert pilot.app.screen.id == DEFAULT_SCREEN_ID

                callback_mock.assert_called_once_with(test_path)

    @pytest.mark.asyncio
    async def test_directory_path_display(self, app, tmp_path):
        """
        Scenario: Directory path display
            Given the modal is displayed
            When I navigate to a directory
            Then the path should be displayed with a trailing slash
        """
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        async with app.run_test() as pilot:
            async with self.file_system_navigation_modal(pilot) as modal:
                assert isinstance(pilot.app.screen, FileSystemNavigationModal)

                event = FileSystemNavigator.ActivePathChanged(test_dir)
                modal.on_active_path_changed(event)

                path_label = modal.query_one("#active-path", Static)
                assert path_label.renderable == "test_dir/"

    @contextlib.asynccontextmanager
    async def file_system_navigation_modal(self, pilot, callback=None):
        if not callback:
            await pilot.app.push_screen(FileSystemNavigationModal())
        else:
            await pilot.app.push_screen(FileSystemNavigationModal(), callback=callback)
        yield pilot.app.screen

    @staticmethod
    def _get_button_by_id(pilot, button_id):
        """
        Retrieve a button component by its ID within the controls.
        Arguments:
            pilot (Pilot): The Pilot test instance.
            button_id (str): The ID of the button to query.
        Returns:
            Button: The found button instance.
        """

        controls = pilot.app.screen.query_one(TestFileSystemNavigationModal.CONTROLS_ID)
        return controls.query_one(button_id)
