import pytest
from textual.widgets import Static

from terry.domain.terraform.core.entities import TerraformInitSettingsAttributes
from terry.presentation.cli.widgets.form.key_value_block import KeyValueBlock
from terry.presentation.cli.screens.tf_init.main import InitSettingsScreen
from tests.integration.utils import click


class TestInitScreen:
    @pytest.mark.asyncio
    async def test_init_settings_screen_open(self, app):
        """
        Scenario: Test InitSettingsScreen opening
        Given the application is running
        When I click on the init button
        Then the init settings screen should be displayed
        """

        header_id = "#header"
        init_button_id = "#init"

        async with app.run_test() as pilot:
            header = pilot.app.query_one(header_id)
            init_button = header.query_one(init_button_id)
            init_button.scroll_visible()
            await click(pilot, init_button)
            assert isinstance(pilot.app.screen, InitSettingsScreen)

    @pytest.mark.asyncio
    async def test_init_settings_screen_creation(self, app):
        """
        Scenario: Test InitSettingsScreen creation
        Given the InitSettingsScreen
        When the screen is mounted
        Then the screen title should be "Init Settings"
        """

        screen = InitSettingsScreen()
        async with app.run_test() as pilot:
            await pilot.app.push_screen(screen)
            assert isinstance(pilot.app.screen, InitSettingsScreen)

            # Verify screen title
            container = screen.query_one("#init_settings")
            assert container.border_title == "Init Settings"

            # Verify description is present
            about = screen.query_one("#about_init", Static)
            assert about is not None

    @pytest.mark.asyncio
    async def test_checkbox_settings(self, app):
        """
        Scenario: Test checkbox settings
        Given the InitSettingsScreen
        When the screen is mounted
        Then all checkbox settings should be present
        """
        screen = InitSettingsScreen()
        async with app.run_test() as pilot:
            await pilot.app.push_screen(screen)

            # Test all checkbox settings
            checkbox_settings = [
                TerraformInitSettingsAttributes.DISABLE_BACKEND,
                TerraformInitSettingsAttributes.FORCE_COPY,
                TerraformInitSettingsAttributes.DISABLE_DOWNLOAD,
                TerraformInitSettingsAttributes.DISABLE_INPUT,
                TerraformInitSettingsAttributes.DISABLE_HOLD_LOCK,
                TerraformInitSettingsAttributes.RECONFIGURE,
                TerraformInitSettingsAttributes.MIGRATE_STATE,
                TerraformInitSettingsAttributes.UPGRADE,
                TerraformInitSettingsAttributes.IGNORE_REMOTE_VERSION,
            ]

            for setting in checkbox_settings:
                checkbox_block = screen.query_one(f"#{setting}")
                assert checkbox_block is not None

    @pytest.mark.asyncio
    async def test_backend_config_section(self, app):
        """
        Scenario: Test backend config section
        Given the InitSettingsScreen
        When the screen is mounted
        Then the backend config section should be present
        """
        screen = InitSettingsScreen()
        async with app.run_test() as pilot:
            await pilot.app.push_screen(screen)

            # Test backend config buttons
            add_config_button = screen.query_one("#add_config_value_button")
            assert add_config_button is not None

            add_config_file_button = screen.query_one("#add_config_file_button")
            assert add_config_file_button is not None

            # Test adding a config value

            await click(pilot, add_config_button)

            key_value_block = screen.query_one(KeyValueBlock)
            assert key_value_block is not None

    @pytest.mark.asyncio
    async def test_directory_selection(self, app):
        """
        Scenario: Test directory selection
        Given the InitSettingsScreen
        When the screen is mounted
        Then the directory selection buttons should be present
        """

        screen = InitSettingsScreen()
        async with app.run_test() as pilot:
            await pilot.app.push_screen(screen)

            # Test plugin directory button
            plugin_dir_button = screen.query_one("#add_plugin_dir_button")
            assert plugin_dir_button is not None

            # Test test directory button
            test_dir_button = screen.query_one("#add_test_dir_button")
            assert test_dir_button is not None

    # @pytest.mark.asyncio
    # async def test_apply_settings(self, app):
    #     """
    #     Scenario: Test applying settings
    #     Given the InitSettingsScreen
    #     When the screen is mounted
    #     Then the settings should be applied
    #     """
    #     screen = InitSettingsScreen()
    #     messages = []
    #     messages_handler = lambda m: messages.append(m)  # noqa
    #     async with app.run_test(message_hook=messages_handler) as pilot:
    #         await pilot.app.push_screen(screen)
    #
    #         # Toggle some checkboxes
    #         upgrade_block = screen.query_one(f"#{TerraformInitSettingsAttributes.UPGRADE}")
    #         await click(pilot, upgrade_block)
    #
    #         reconfigure_block = screen.query_one(f"#{TerraformInitSettingsAttributes.RECONFIGURE}")
    #         await click(pilot, reconfigure_block)
    #
    #         # Add a backend config
    #         add_config_button = screen.query_one("#add_config_value_button")
    #         await click(pilot, add_config_button)
    #
    #         # Apply settings
    #         apply_button = screen.query_one("#apply")
    #         await pilot.click(apply_button)
    #
    #         # Verify the generated request
    #         init_requests = [m for m in messages if isinstance(m, InitActionRequest)]
    #         assert len(init_requests) == 1
    #
    #         settings = init_requests[0].settings
    #         assert settings.upgrade is True
    #         assert settings.reconfigure is True
    #         assert settings.backend_config == []
    #         assert settings.backend_config_path == []
    #         assert settings.plugin_dir == []
    #         assert settings.test_directory == []

    @pytest.mark.asyncio
    async def test_close_screen(self, app):
        """
        Scenario: Test closing the screen
        Given the InitSettingsScreen
        When the screen is mounted
        Then the screen should be closed
        """
        screen = InitSettingsScreen()
        async with app.run_test() as pilot:
            # Test close button
            await pilot.app.push_screen(screen)
            close_button = screen.query_one("#close")
            await click(pilot, close_button)
            assert pilot.app.screen is not screen

            # Test escape key
            await pilot.app.push_screen(screen)
            await pilot.press("escape")
            await pilot.pause()
            assert pilot.app.screen is not screen
