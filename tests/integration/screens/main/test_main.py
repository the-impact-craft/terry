from unittest.mock import patch

import pytest
from watchdog.events import FileSystemEvent, EVENT_TYPE_MODIFIED, EVENT_TYPE_CREATED

from terry.presentation.cli.messages.tf_format_action_request import FormatActionRequest
from terry.presentation.cli.screens.tf_format.main import FormatScope
from terry.presentation.cli.screens.main.containers.content import Content
from terry.settings import DEFAULT_THEME

WORKSPACES_COMPONENT_ID = "#workspaces"
WORKSPACES_RADIO_SET_ID = "#workspaces_radio_set"
FORMAT_ACTION_PARAMS = FormatScope("Apply to current file", "ctrl+t+f", True, "current_file")
COMPONENT_IDS = [
    "workspaces",
    "project_tree",
    "state_files",
    "content",
    "commands_log",
]


def create_file_system_event(src_path, event_type, is_directory):
    file_system_event = FileSystemEvent(src_path, src_path)
    file_system_event.event_type = event_type
    file_system_event.is_directory = is_directory
    return file_system_event


class TestTerryApp:
    """
    Feature: Terry Main Screen
        As a user
        I want to interact with the Terry interface
        So that I can manage Terraform configurations effectively
    """

    @pytest.mark.asyncio
    async def test_main_screen(self, app):
        """
        Scenario: Viewing and selecting Terraform files
            Given the Terry application is launched
            Then the main screen is displayed with "github-dark" theme
            And workspaces, project_tree, state_files, console_log and preview content component are rendered

        """
        async with app.run_test() as pilot:
            assert app.theme == DEFAULT_THEME
            for component_id in COMPONENT_IDS:
                assert pilot.app.query_one(f"#{component_id}") is not None

    @pytest.mark.asyncio
    async def test_format_current_file_with_no_opened_file_request(self, app):
        """
        Scenario: Format request
            Given the application is running
            When I request to format the current file
            Then the format action should not be executed
        """
        async with app.run_test() as pilot:
            # Publish the format request
            pilot.app.post_message(FormatActionRequest(FORMAT_ACTION_PARAMS))

            await pilot.pause()
            pilot.app.terraform_core_service.fmt.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_selected_file_content(self, app):
        """
        Scenario: Update selected file content
            Given the application is running
            When update_selected_file_content with FileSystemEvent was triggered with file entity
            Then the content_tabs.update should be called
        """
        file_name = "test.tf"
        file_content = "test content"
        modified_file = app.work_dir / file_name
        modified_file.write_text(file_content)

        async with app.run_test() as pilot:
            file_entity = create_file_system_event(modified_file, EVENT_TYPE_MODIFIED, False)

            content_tabs = pilot.app.query_one(Content)
            content_tabs.files_contents = {file_name: modified_file}

            pilot.app.file_system_service.read.return_value = file_content
            with patch.object(content_tabs, "update") as update_mock:
                pilot.app.update_selected_file_content(file_entity)
                update_mock.assert_called_once_with(file_name, file_content)

    @pytest.mark.parametrize(
        "file_system_event,tab_files_content,create_file",
        [
            ("test1.tf", {"test1.tf": ""}, False),
            (create_file_system_event("test1.tf", EVENT_TYPE_MODIFIED, True), {"test1.tf": ""}, False),
            (create_file_system_event("test2.tf", EVENT_TYPE_CREATED, False), {"test2.tf": ""}, False),
            (create_file_system_event("test.tf", EVENT_TYPE_MODIFIED, False), {}, True),
        ],
    )
    @pytest.mark.asyncio
    async def test_update_selected_file_content_with_wrong_file_entity(
        self, app, file_system_event, tab_files_content, create_file
    ):
        """
        Scenario: Update selected file content
            Given the application is running
            When update_selected_file_content with FileSystemEvent was triggered with no file entity
            Then the content_tabs.update should not be called
        """
        if create_file:
            file_name = file_system_event.src_path
            modified_file = app.work_dir / file_name
            modified_file.touch()
            file_system_event.src_path = modified_file

        async with app.run_test() as pilot:
            content_tabs = pilot.app.query_one(Content)
            content_tabs.files_contents = tab_files_content
            with patch.object(content_tabs, "update") as update_mock:
                pilot.app.update_selected_file_content(file_system_event)
                update_mock.assert_not_called()
