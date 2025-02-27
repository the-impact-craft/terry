import pytest
from textual.widgets import Static

from terry.domain.terraform.core.entities import TerraformValidateSettingsAttributes, ValidateSettings
from terry.presentation.cli.messages.tf_validate_action_request import ValidateActionRequest
from terry.presentation.cli.screens.tf_validate.main import ValidateSettingsScreen
from tests.integration.utils import click


class TestValidateScreen:
    @pytest.mark.asyncio
    async def test_validate_settings_screen_open(self, app):
        """
        Scenario: Test ValidateSettingsScreen opening
        Given the application is running
        When I click on the validate button
        Then the validate settings screen should be displayed
        """

        header_id = "#header"
        init_button_id = "#validate"

        async with app.run_test() as pilot:
            header = pilot.app.query_one(header_id)
            validate_button = header.query_one(init_button_id)
            validate_button.scroll_visible()
            await click(pilot, validate_button)
            assert isinstance(pilot.app.screen, ValidateSettingsScreen)

    @pytest.mark.asyncio
    async def test_validate_settings_screen_creation(self, app):
        """
        Scenario: Test ValidateSettingsScreen creation
        Given the ValidateSettingsScreen
        When the screen is mounted
        Then the screen title should be "Validate Settings"
        And the description should be present
        And Validate the configuration files should be in the description
        """
        screen = ValidateSettingsScreen()
        async with app.run_test() as pilot:
            await pilot.app.push_screen(screen)
            assert isinstance(pilot.app.screen, ValidateSettingsScreen)

            # Verify screen container
            container = screen.query_one("#validate_settings")
            assert container is not None

            # Verify description
            about = screen.query_one("#about_validate", Static)
            assert about is not None
            assert "Validate the configuration files" in about.renderable

    @pytest.mark.asyncio
    async def test_settings_section(self, app):
        """
        Scenario: Test settings section
        Given the ValidateSettingsScreen
        When the screen is mounted
        Then the settings section should be present
        """
        screen = ValidateSettingsScreen()
        async with app.run_test() as pilot:
            await pilot.app.push_screen(screen)

            # Verify settings scroll container
            settings = screen.query_one("#settings")
            assert settings is not None

            # Verify no-tests checkbox
            no_tests_block = screen.query_one(f"#{TerraformValidateSettingsAttributes.NO_TESTS}")
            assert no_tests_block is not None

    @pytest.mark.asyncio
    async def test_test_directory_selection(self, app):
        """Test test directory selection functionality"""
        screen = ValidateSettingsScreen()
        async with app.run_test() as pilot:
            await pilot.app.push_screen(screen)

            # Verify test directory section
            test_dir_section = screen.query_one(f"#{TerraformValidateSettingsAttributes.TEST_DIRECTORY}")
            assert test_dir_section is not None

            # Verify add directory button
            add_dir_button = screen.query_one("#add_test_dir_button")
            assert add_dir_button is not None
            assert "+ Add Test Directory" in add_dir_button.renderable

    @pytest.mark.asyncio
    async def test_control_labels(self, app):
        """Test control labels presence and functionality"""
        screen = ValidateSettingsScreen()
        async with app.run_test() as pilot:
            await pilot.app.push_screen(screen)

            # Verify controls container
            controls = screen.query_one("#controls")
            assert controls is not None

            # Verify close button
            close_button = screen.query_one("#close")
            assert close_button is not None
            assert "Close" in close_button.renderable

            # Verify apply button
            apply_button = screen.query_one("#apply")
            assert apply_button is not None
            assert "Apply" in apply_button.renderable

    @pytest.mark.asyncio
    async def test_settings_application(self, app):
        """Test settings application and request generation"""
        screen = ValidateSettingsScreen()
        messages = []
        messages_handler = lambda m: messages.append(m)  # noqa
        async with app.run_test(message_hook=messages_handler) as pilot:
            await pilot.app.push_screen(screen)

            # Toggle no-tests setting
            no_tests_block = screen.query_one(f"#{TerraformValidateSettingsAttributes.NO_TESTS}")
            await pilot.click(no_tests_block)

            # Apply settings
            apply_button = screen.query_one("#apply")
            await pilot.click(apply_button)

            # Verify the generated request
            validate_requests = [m for m in messages if isinstance(m, ValidateActionRequest)]
            assert len(validate_requests) == 1

            settings = validate_requests[0].settings
            assert isinstance(settings, ValidateSettings)
            assert settings.no_tests is True
            assert settings.test_directory == []

    @pytest.mark.asyncio
    async def test_screen_closing(self, app):
        """Test screen closing functionality"""
        screen = ValidateSettingsScreen()
        async with app.run_test() as pilot:
            await pilot.app.push_screen(screen)

            # Test close button
            close_button = screen.query_one("#close")
            await pilot.click(close_button)
            assert pilot.app.screen is not screen

            # Test escape key
            await pilot.app.push_screen(screen)
            await pilot.press("escape")
            assert pilot.app.screen is not screen
