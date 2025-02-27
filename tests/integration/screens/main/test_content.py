from pathlib import Path

import pytest
from textual.widgets import TextArea

from terry.presentation.cli.messages.files_select_message import FileSelect
from terry.settings import ANIMATION_SPEED
from tests.integration.utils import click


class TestContent:
    """
    Feature: File Content Management
    As a user
    I want to manage multiple file tabs and preview content
    So that I can view and edit Terraform files
    """

    @pytest.mark.asyncio
    async def test_content_initialization(self, app):
        """
        Scenario: Initialize content component
            Given the content component is mounted
            Then the component should have a "Content" border title
            And a TabbedContent widget should be present
            And no tabs should be open initially
        """
        async with app.run_test() as pilot:
            content = pilot.app.query_one("#content")
            tabbed_content = content.query_one("#tabbed-content")

            assert content.border_title is None
            assert tabbed_content.tab_count == 0

    @pytest.mark.asyncio
    async def test_add_file_tab(self, app, file_system_service):
        """
        Scenario: Add new file tab
            Given the content component is mounted
            When I add a new file "main.tf"
            Then a new tab should be created
            And the file content should be displayed
            And the tab should have correct title and ID
        """
        async with app.run_test() as pilot:
            content = pilot.app.query_one("#content")
            tabbed_content = content.query_one("#tabbed-content")

            # Simulate adding a new file
            file_path = Path("main.tf")
            file_content = "resource 'aws_instance' 'example' {}"
            file_system_service.read.return_value = file_content
            await pilot.app.on_file_select(FileSelect(file_path))

            tab_id = content.files_contents[str(file_path)].get("id")

            assert tabbed_content.tab_count == 1
            tab = tabbed_content.active_tab
            assert tab is not None
            assert str(tab.label) == "main.tf"
            assert tab.id == tab_id

    @pytest.mark.asyncio
    async def test_add_json_file_tab(self, app, file_system_service):
        """
        Scenario: Add new file tab
            Given the content component is mounted
            When I add a new file "main.tf"
            Then a new tab should be created
            And the file content should be displayed
            And the tab should have correct title and ID
        """
        async with app.run_test() as pilot:
            content = pilot.app.query_one("#content")
            tabbed_content = content.query_one("#tabbed-content")
            content_preview = content.query_one("#content-preview")

            # Simulate adding a new file
            file_path = Path("main.json")
            file_content = '{"key": ["value"], "key2": "value2"}'
            file_system_service.read.return_value = file_content

            await pilot.app.on_file_select(FileSelect(file_path))
            await pilot.pause()

            tab_id = content.files_contents[str(file_path)].get("id")
            tab = tabbed_content.active_tab

            assert tabbed_content.tab_count == 1
            assert tab is not None
            assert str(tab.label) == "main.json"
            assert tab.id == tab_id
            assert content_preview.query_one("#json-preview") is not None

    @pytest.mark.asyncio
    async def test_close_all_tabs(self, app, file_system_service):
        """
        Scenario: Close file tab
            Given a file tab is open
            When I press close all (c)
            Then the all tabs should be removed
            And the file content should be cleared
        """
        async with app.run_test() as pilot:
            content = pilot.app.query_one("#content")
            tabbed_content = content.query_one("#tabbed-content")
            content_preview = content.query_one("#content-preview")

            files = {"main.tf": "resource 'aws_instance' 'example' {}", "variables.tf": "variable 'region' {}"}

            for file_path, file_content in files.items():
                file_system_service.read.return_value = file_content
                await pilot.app.on_file_select(FileSelect(Path(file_path)))

            # Activate content area
            await click(pilot, tabbed_content)

            # Close the tab
            await pilot.press("c")

            # Assert tab has been removed
            assert tabbed_content.tab_count == 0
            assert len(content.files_contents) == 0
            assert content_preview.query_one("#no_content_label_content") is not None

    @pytest.mark.asyncio
    async def test_close_file_tab(self, app, file_system_service):
        """
        Scenario: Close file tab
            Given a file tab is open
            When I click the close button
            Then the tab should be removed
            And the file content should be cleared
        """
        async with app.run_test() as pilot:
            content = pilot.app.query_one("#content")
            tabbed_content = content.query_one("#tabbed-content")

            # Add a file first
            file_path = Path("main.tf")
            file_content = "resource 'aws_instance' 'example' {}"
            file_system_service.read.return_value = file_content
            await pilot.app.on_file_select(FileSelect(file_path))

            # Assert tab has been added
            assert tabbed_content.tab_count == 1

            # Activate the tab component
            await click(pilot, tabbed_content)

            # Close the tab
            await pilot.press("r")

            # Assert tab has been removed
            assert tabbed_content.tab_count == 0

    @pytest.mark.asyncio
    async def test_switch_between_tabs(self, app, file_system_service):
        """
        Scenario: Switch between multiple tabs
            Given multiple file tabs are open
            When I click on a different tab
            Then that tab should become active
            And its content should be displayed
        """
        async with app.run_test() as pilot:
            content = pilot.app.query_one("#content")
            tabbed_content = content.query_one("#tabbed-content")

            # Add two files
            files = {"main.tf": "resource 'aws_instance' 'example' {}", "variables.tf": "variable 'region' {}"}

            for file_path, file_content in files.items():
                file_system_service.read.return_value = file_content
                await pilot.app.on_file_select(FileSelect(Path(file_path)))

            # Activate content area
            await click(pilot, tabbed_content)

            # Switch tabs
            for file_name in files:
                tab_id = content.files_contents.get(file_name).get("id", "")
                await pilot.click(f"#{tab_id}")

                tab = tabbed_content.active_tab
                assert tab is not None
                assert str(tab.label) == file_name
                assert tab.id == tab_id

    @pytest.mark.asyncio
    async def test_no_content(self, app):
        """
        Scenario: No content to display
            Given no file is selected
            When the content component is mounted
            Then a message should be displayed
        """
        async with app.run_test() as pilot:
            content = pilot.app.query_one("#content")
            content_preview = content.query_one("#content-preview")

            no_content_placeholder = content_preview.query_one("#no_content_label_content")
            assert no_content_placeholder is not None
            content1 = no_content_placeholder.renderable
            await pilot.pause(ANIMATION_SPEED * 2)
            content2 = no_content_placeholder.renderable
            assert content1 != content2

    @pytest.mark.asyncio
    async def test_update_file_tab(self, app, file_system_service):
        """
        Scenario: Update file tab content
            Given a file tab is open
            When I update the file content
            Then the tab content should be updated
        """
        async with app.run_test() as pilot:
            content = pilot.app.query_one("#content")

            # Simulate adding a new file
            file_path = Path("main.tf")
            initial_file_content = "resource 'aws_instance' 'example' {}"
            updated_content = "resource 'aws_instance' 'example' {name = 'test'}"

            file_system_service.read.return_value = initial_file_content
            await pilot.app.on_file_select(FileSelect(file_path))
            await pilot.pause()

            text_area = content.query_one(TextArea)
            assert initial_file_content == text_area.document.text

            content.update("main.tf", updated_content)
            await pilot.pause()

            text_area = content.query_one(TextArea)
            assert updated_content == text_area.document.text

    @pytest.mark.asyncio
    async def test_update_file_tab_with_empty_tabs(self, app, file_system_service):
        """
        Scenario: Update file tab content
            Given a file tab is open
            When I update the file content
            Then the tab content should be updated
        """
        async with app.run_test() as pilot:
            content = pilot.app.query_one("#content")
            tabbed_content = content.query_one("#tabbed-content")
            assert tabbed_content.tab_count == 0
            # Simulate adding a new file

            updated_content = "resource 'aws_instance' 'example' {name = 'test'}"
            content.update("main.tf", updated_content)
            await pilot.pause()

            assert tabbed_content.tab_count == 0

    @pytest.mark.asyncio
    async def test_update_not_active_file_tab(self, app, file_system_service):
        """
        Scenario: Update file not active tab content
            Given a file tab is open
            When I update the file content
            Then the active tab content should not be updated
            And cashed content should be updated
        """
        async with app.run_test() as pilot:
            content = pilot.app.query_one("#content")

            # Simulate adding a new file
            file_path_1 = Path("main.tf")
            file_path_2 = Path("main2.tf")
            initial_file_content = "resource 'aws_instance' 'example' {}"
            updated_content = "resource 'aws_instance' 'example' {name = 'test'}"

            file_system_service.read.return_value = initial_file_content
            await pilot.app.on_file_select(FileSelect(file_path_1))
            await pilot.pause()

            await pilot.app.on_file_select(FileSelect(file_path_2))
            await pilot.pause()

            text_area = content.query_one(TextArea)
            assert initial_file_content == text_area.document.text

            content.update("main.tf", updated_content)
            await pilot.pause()

            text_area = content.query_one(TextArea)
            assert initial_file_content == text_area.document.text
            assert content.files_contents["main.tf"]["content"] == updated_content
