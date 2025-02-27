import pytest
from textual.widgets import Static

from terry.domain.terraform.core.entities import TerraformApplySettingsAttributes
from terry.presentation.cli.screens.tf_apply.main import ApplySettingsScreen
from tests.integration.utils import click


class TestApplyScreen:
    @pytest.mark.asyncio
    async def test_apply_settings_screen_open(self, app):
        """
        Scenario: Test ApplySettingsScreen opening
        Given the application is running
        When I click on the apply button
        Then the apply settings screen should be displayed
        """

        header_id = "#header"
        init_button_id = "#apply"

        async with app.run_test() as pilot:
            header = pilot.app.query_one(header_id)
            apply_button = header.query_one(init_button_id)
            apply_button.scroll_visible()
            await click(pilot, apply_button)
            assert isinstance(pilot.app.screen, ApplySettingsScreen)

    @pytest.mark.asyncio
    async def test_apply_settings_screen_creation(self, app):
        """Test that the ApplySettingsScreen can be created and mounted"""

        screen = ApplySettingsScreen()
        async with app.run_test() as pilot:
            await pilot.app.push_screen(screen)
            assert isinstance(pilot.app.screen, ApplySettingsScreen)

            # Verify screen container
            container = screen.query_one("#apply_settings")
            assert container is not None
            assert container.border_title == "Apply Settings"

            # Verify description
            about = screen.query_one("#about_apply", Static)
            assert about is not None
            assert "Creates or updates infrastructure according to Terraform" in about.renderable

    @pytest.mark.asyncio
    async def test_checkbox_settings(self, app):
        """Test checkbox settings presence and functionality"""

        screen = ApplySettingsScreen()
        async with app.run_test() as pilot:
            await pilot.app.push_screen(screen)

            # Verify all checkboxes
            checkbox_settings = [
                TerraformApplySettingsAttributes.AUTO_APPROVE,
                TerraformApplySettingsAttributes.DESTROY,
                TerraformApplySettingsAttributes.DISABLE_BACKUP,
                TerraformApplySettingsAttributes.DISABLE_LOCK,
                TerraformApplySettingsAttributes.INPUT,
            ]

            for setting in checkbox_settings:
                checkbox_block = screen.query_one(f"#{setting}")
                assert checkbox_block is not None

    @pytest.mark.asyncio
    async def test_text_input_settings(self, app):
        """Test text input settings presence"""

        screen = ApplySettingsScreen()
        async with app.run_test() as pilot:
            await pilot.app.push_screen(screen)

            # Verify text input fields
            text_inputs = [TerraformApplySettingsAttributes.BACKUP, TerraformApplySettingsAttributes.STATE_OUT]

            for input_id in text_inputs:
                input_block = screen.query_one(f"#{input_id}")
                assert input_block is not None

    @pytest.mark.asyncio
    async def test_state_file_selection(self, app):
        """Test state file selection functionality"""

        screen = ApplySettingsScreen()
        async with app.run_test() as pilot:
            await pilot.app.push_screen(screen)

            # Verify state file section
            state_section = screen.query_one(f"#{TerraformApplySettingsAttributes.STATE}")
            assert state_section is not None

            # Verify add state file button
            add_state_button = screen.query_one("#add_state_path")
            assert add_state_button is not None
            assert "+ State file path" in add_state_button.renderable

    @pytest.mark.asyncio
    async def test_control_buttons(self, app):
        """Test control buttons presence and functionality"""

        screen = ApplySettingsScreen()
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

    # @pytest.mark.asyncio
    # async def test_settings_application(self, app):
    #     """Test settings application and request generation"""
    #     messages = []
    #     messages_handler = lambda m: messages.append(m)  # noqa
    #     screen = ApplySettingsScreen()
    #     async with app.run_test(message_hook=messages_handler) as pilot:
    #         await pilot.app.push_screen(screen)
    #
    #         # Configure checkbox settings
    #         auto_approve_block = screen.query_one(f"#{TerraformApplySettingsAttributes.AUTO_APPROVE}")
    #         await click(pilot, auto_approve_block)
    #
    #         destroy_block = screen.query_one(f"#{TerraformApplySettingsAttributes.DESTROY}")
    #         await click(pilot, destroy_block)
    #         # Apply settings
    #         apply_button = screen.query_one("#apply")
    #         await click(pilot, apply_button)
    #
    #         # Verify the generated request
    #         apply_requests = [m for m in messages if isinstance(m, ApplyActionRequest)]
    #         assert len(apply_requests) == 1
    #
    #         settings = apply_requests[0].settings
    #         assert isinstance(settings, ApplySettings)
    #         assert settings.auto_approve is True
    #         assert settings.destroy is True
    #         assert settings.disable_backup is False
    #         assert settings.disable_lock is False
    #         assert settings.input is False
    #         assert settings.backup == ""
    #         assert settings.state_out == ""
    #         assert settings.state == []

    @pytest.mark.asyncio
    async def test_screen_closing(self, app):
        """Test screen closing functionality"""

        screen = ApplySettingsScreen()
        async with app.run_test() as pilot:
            await pilot.app.push_screen(screen)

            # Test close button
            close_button = screen.query_one("#close")
            await click(pilot, close_button)
            assert pilot.app.screen is not screen

            # Test escape key
            await pilot.app.push_screen(screen)
            await pilot.press("escape")
            await pilot.pause()
            assert pilot.app.screen is not screen
