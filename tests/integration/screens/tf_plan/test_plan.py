from unittest.mock import patch

import pytest

from terry.domain.terraform.core.entities import TerraformPlanSettingsAttributes
from terry.presentation.cli.widgets.buttons.add_key_value_button import AddKeyValueButton
from terry.presentation.cli.widgets.buttons.delete_button import DeleteButton
from terry.presentation.cli.widgets.buttons.open_file_navigator_modal_button import FileNavigatorModalButton
from terry.presentation.cli.widgets.buttons.view_secret_field_button import ViewSecretFieldButton
from terry.presentation.cli.widgets.clickable_icon import ClickableIcon
from terry.presentation.cli.widgets.form.file_selection_block import FileSelectionBlock
from terry.presentation.cli.widgets.form.key_value_block import KeyValueBlock
from terry.presentation.cli.screens.file_system_navigation.main import FileSystemNavigationModal
from terry.presentation.cli.screens.tf_plan.main import PlanSettingsScreen
from tests.integration.utils import DEFAULT_SCREEN_ID, enter, click


class TestPlanScreen:
    """
    Feature: Terraform Plan Screen
       As a user
       I want to configure and execute Terraform plan
       So that I can preview changes before applying them
    """

    # Constants for element IDs
    CONTROLS_ID = "#controls"
    CLOSE_BUTTON_ID = "#close"
    APPLY_BUTTON_ID = "#apply"
    HEADER_ID = "#header"
    PLAN_BUTTON_ID = "#plan"

    @pytest.mark.asyncio
    async def test_open_plan_screen_success(self, app):
        """
        Scenario: Successfully opening plan settings screen
            Given the application is running
            And environment variables are available
            When I trigger the plan action
            Then the plan settings screen should be displayed
            And environment variables should be loaded
        """
        async with app.run_test() as pilot:
            # Trigger plan action
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

    @pytest.mark.asyncio
    async def test_mode_settings_interactions(self, app):
        """
        Scenario: Configuring mode settings
            Given the plan settings screen is open
            When I toggle different mode settings
            Then the settings should be updated accordingly
        """
        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            # Toggle mode settings
            destroy_checkbox = pilot.app.screen.query_one("#destroy")
            refresh_only_checkbox = pilot.app.screen.query_one("#refresh_only")
            norefresh_checkbox = pilot.app.screen.query_one("#norefresh")

            destroy_checkbox.toggle()
            refresh_only_checkbox.toggle()
            norefresh_checkbox.toggle()

            assert destroy_checkbox.value is True
            assert refresh_only_checkbox.value is True
            assert norefresh_checkbox.value is True

    @pytest.mark.asyncio
    async def test_environment_variables_management(self, app):
        """
        Scenario: Managing environment variables
            Given the plan settings screen is open
            When I add and modify environment variables
            Then the variables should be properly managed
        """
        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            # Test system env variables
            env_vars_container = self._get_env_vars_container(pilot.app.screen)
            var_block = env_vars_container.query(KeyValueBlock).first()
            value_input = var_block.children[1]

            # Toggle visibility click
            view_button = var_block.query_one(ViewSecretFieldButton)
            await click(pilot, view_button)
            assert value_input.password is False

            # Toggle visibility enter key
            await enter(pilot, view_button)
            assert value_input.password is True
            system_vars_number = len(list(env_vars_container.query(KeyValueBlock).results()))

            # Test new environment variable
            add_button = self.get_add_key_value_button(env_vars_container)
            await click(pilot, add_button)
            assert len(list(env_vars_container.query(KeyValueBlock).results())) == system_vars_number + 1

            # Delete the variable
            var_block = env_vars_container.query(KeyValueBlock).last()
            delete_button = var_block.query_one(DeleteButton)
            await click(pilot, delete_button)
            assert len(list(env_vars_container.query(KeyValueBlock).results())) == system_vars_number

    @pytest.mark.asyncio
    async def test_add_env_vars_button(self, app):
        """
        Scenario: Adding environment variables
            Given the plan settings screen is open
            When I add environment variables clicking on the button
            Then the variables should be properly added
        """

        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            env_vars_container = self._get_env_vars_container(pilot.app.screen)
            add_env_var_button = self.get_add_key_value_button(env_vars_container)

            vars_number = len(list(env_vars_container.query(KeyValueBlock).results()))

            # Test clicking on the button
            await click(pilot, add_env_var_button)
            time_out = 4
            for i in range(time_out):
                if len(list(env_vars_container.query(KeyValueBlock).results())) == vars_number + 1:
                    break
                await pilot.pause(i)

            assert len(list(env_vars_container.query(KeyValueBlock).results())) == vars_number + 1

    @pytest.mark.asyncio
    async def test_add_env_vars_enter(self, app):
        """
        Scenario: Adding environment variables
            Given the plan settings screen is open
            When I add environment variables clicking on pressing the enter
            Then the variables should be properly added
        """

        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            env_vars_container = self._get_env_vars_container(pilot.app.screen)
            add_env_var_button = self.get_add_key_value_button(env_vars_container)

            vars_number = len(list(env_vars_container.query(KeyValueBlock).results()))

            # Test pressing the enter
            await enter(pilot, add_env_var_button)

            assert len(list(env_vars_container.query(KeyValueBlock).results())) == vars_number + 1

    @pytest.mark.asyncio
    async def test_delete_env_var_block_with_click(self, app):
        """
        Scenario: Deleting an environment variable block
            Given the plan settings screen is open
            When I delete an environment variable block with a click
            Then the block should be removed
        """
        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            # Test system env variables
            env_vars_container = self._get_env_vars_container(pilot.app.screen)
            add_env_var_button = self.get_add_key_value_button(env_vars_container)

            system_vars_number = len(list(env_vars_container.query(KeyValueBlock).results()))

            await click(pilot, add_env_var_button)

            assert len(list(env_vars_container.query(KeyValueBlock).results())) == system_vars_number + 1

            # Delete the variable
            var_block = env_vars_container.query(KeyValueBlock).last()
            delete_button = var_block.children[-1]

            delete_button.scroll_visible()

            await click(pilot, delete_button)

            assert len(list(env_vars_container.query(KeyValueBlock).results())) == system_vars_number

    @pytest.mark.asyncio
    async def test_delete_env_var_block_with_key(self, app):
        """
        Scenario: Deleting an environment variable block
            Given the plan settings screen is open
            When I delete an environment variable block with a backspace key
            Then the block should be removed
        """
        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            # Test system env variables
            env_vars_container = self._get_env_vars_container(pilot.app.screen)
            add_env_var_button = self.get_add_key_value_button(env_vars_container)

            system_vars_number = len(list(env_vars_container.query(KeyValueBlock).results()))

            await click(pilot, add_env_var_button)
            await pilot.pause()

            time_out = 5
            for i in range(time_out):
                if len(list(env_vars_container.query(KeyValueBlock).results())) == system_vars_number + 1:
                    break
                await pilot.pause(i)

            assert len(list(env_vars_container.query(KeyValueBlock).results())) == system_vars_number + 1

            # Delete the variable
            var_block = env_vars_container.query(KeyValueBlock).last()
            delete_button = var_block.children[-1]

            delete_button.scroll_visible()
            delete_button.focus()
            await pilot.press("backspace")
            await pilot.pause()

            assert len(list(env_vars_container.query(KeyValueBlock).results())) == system_vars_number

    @pytest.mark.asyncio
    async def test_inline_variables_management(self, app):
        """
        Scenario: Managing inline variables
            Given the plan settings screen is open
            When I add and modify inline variables
            Then the variables should be properly managed
        """
        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            inline_vars_container = self._get_inline_vars_container(pilot.app.screen)
            add_inline_var_button = self.get_add_key_value_button(inline_vars_container)

            # Add new inline variable
            await click(pilot, add_inline_var_button)

            var_block = inline_vars_container.query(KeyValueBlock).first()

            # Fill in the values
            key_input = var_block.children[0]
            value_input = var_block.children[1]

            key_input.value = "region"
            value_input.value = "us-west-2"

            assert len(list(inline_vars_container.query(KeyValueBlock).results())) == 1

    @pytest.mark.asyncio
    async def test_add_inline_vars_button(self, app):
        """
        Scenario: Adding inline variables
            Given the plan settings screen is open
            When I add inline variables clicking on the button
            Then the variables should be properly added
        """

        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            inline_vars_container = self._get_inline_vars_container(pilot.app.screen)
            add_inline_var_button = self.get_add_key_value_button(inline_vars_container)

            vars_number = len(list(inline_vars_container.query(KeyValueBlock).results()))

            # Test clicking on the button
            await click(pilot, add_inline_var_button)

            assert len(list(inline_vars_container.query(KeyValueBlock).results())) == vars_number + 1

    @pytest.mark.asyncio
    async def test_add_inline_vars_enter(self, app):
        """
        Scenario: Adding inline variables
            Given the plan settings screen is open
            When I add inline variables clicking on pressing the enter
            Then the variables should be properly added
        """

        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            inline_vars_container = self._get_inline_vars_container(pilot.app.screen)
            add_inline_var_button = inline_vars_container.query_one(AddKeyValueButton)

            vars_number = len(list(inline_vars_container.query(KeyValueBlock).results()))

            # Test pressing the enter
            add_inline_var_button.scroll_visible()
            await enter(pilot, add_inline_var_button)

            assert len(list(inline_vars_container.query(KeyValueBlock).results())) == vars_number + 1

    @pytest.mark.asyncio
    async def test_variable_files_management(self, app, tmp_path):
        """
        Scenario: Managing variable files
            Given the plan settings screen is open
            When I add variable files
            Then the files should be properly managed
        """
        # Create a temporary tfvars file
        var_file = tmp_path / "test.tfvars"
        var_file.write_text('region = "us-west-2"')

        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            # Simulate file selection
            event = FileNavigatorModalButton.Click(
                button_id="add_var_file_button",
                section_id=TerraformPlanSettingsAttributes.VAR_FILES,
                file_path=var_file,
            )
            pilot.app.screen.add_file_block(event)

            env_var_files_container = self._get_var_files_container(pilot.app.screen)
            assert len(list(env_var_files_container.query(FileSelectionBlock).results())) == 1

    @pytest.mark.asyncio
    async def test_add_file_vars_button(self, app):
        """
        Scenario: Adding file variables
            Given the plan settings screen is open
            When I add variables file clicking on the button
            Then the variables should be properly added
        """

        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            env_var_files_container = self._get_var_files_container(pilot.app.screen)
            add_env_var_files_button = env_var_files_container.query_one(FileNavigatorModalButton)

            # Test clicking on the button
            add_env_var_files_button.scroll_visible()
            await click(pilot, add_env_var_files_button)

            assert isinstance(pilot.app.screen, FileSystemNavigationModal)

    @pytest.mark.asyncio
    async def test_add_file_vars_enter(self, app):
        """
        Scenario: Adding file variables
            Given the plan settings screen is open
            When I add variables file clicking on pressing enter
            Then the variables should be properly added
        """

        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            env_var_files_container = self._get_var_files_container(pilot.app.screen)
            add_env_var_files_button = env_var_files_container.query_one(FileNavigatorModalButton)

            # Test clicking on the button
            add_env_var_files_button.scroll_visible()
            await enter(pilot, add_env_var_files_button)

            assert isinstance(pilot.app.screen, FileSystemNavigationModal)

    @pytest.mark.asyncio
    async def test_apply_settings_with_all_options(self, app):
        """
        Scenario: Applying plan settings with all options
            Given the plan settings screen is open
            When I configure all available options
            And apply the settings
            Then the settings should be properly collected and applied
        """

        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            # Configure mode settings
            destroy_checkbox = pilot.app.screen.query_one(f"#{TerraformPlanSettingsAttributes.DESTROY}")
            destroy_checkbox.toggle()

            # Add environment variable
            env_vars_container = self._get_env_vars_container(pilot.app.screen)
            add_env_var_button = self.get_add_key_value_button(env_vars_container)

            add_env_var_button.scroll_visible()
            await click(pilot, add_env_var_button)

            env_var_block = env_vars_container.query(KeyValueBlock).first()
            env_var_block.children[0].value = "ENV_VAR"
            env_var_block.children[1].value = "env_value"

            # Add inline variable
            inline_vars_container = self._get_inline_vars_container(pilot.app.screen)
            add_inline_var_button = self.get_add_key_value_button(inline_vars_container)

            await click(pilot, add_inline_var_button)

            inline_var_block = inline_vars_container.query(KeyValueBlock).first()
            inline_var_block.children[0].value = "inline_var"
            inline_var_block.children[1].value = "inline_value"

            # Verify the settings were applied

            apply_button = self._get_button_by_id(pilot, self.APPLY_BUTTON_ID)
            with patch("terry.presentation.cli.screens.main.main.Terry.run_tf_action") as mock:
                await click(pilot, apply_button)
                mock.assert_called()

    @pytest.mark.asyncio
    async def test_close(self, app):
        """
        Scenario: Closing plan settings screen
            Given the plan settings screen is open
            When I close the screen
            Then the screen should be closed
        """

        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            close_button = self._get_button_by_id(pilot, self.CLOSE_BUTTON_ID)

            await click(pilot, close_button)
            assert pilot.app.screen.id == DEFAULT_SCREEN_ID

    @pytest.mark.asyncio
    async def test_absent_toggle_button(self, app):
        """
        Scenario: Toggling an absent button
            Given the plan settings screen is open
            When I toggle an absent button
            Then the screen should remain unchanged
        """
        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            destroy_checkbox = pilot.app.screen.query_one("#destroy")
            destroy_checkbox.remove()

            apply_button = self._get_button_by_id(pilot, self.APPLY_BUTTON_ID)
            with patch("terry.presentation.cli.screens.main.main.Terry.run_tf_action") as mock:
                await click(pilot, apply_button)
                mock.assert_not_called()
            self._assert_screen_is_plan_settings(pilot)

    @pytest.mark.asyncio
    async def test_absent_env_var_button(self, app):
        """
        Scenario: Toggling an absent button
            Given the plan settings screen is open
            When I toggle an absent button
            Then the screen should remain unchanged
        """
        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            env_vars_block = self._get_env_vars_container(pilot.app.screen)
            env_vars_block.remove()

            apply_button = self._get_button_by_id(pilot, self.APPLY_BUTTON_ID)
            with patch("terry.presentation.cli.screens.main.main.Terry.run_tf_action") as mock:
                await click(pilot, apply_button)
                mock.assert_not_called()
            self._assert_screen_is_plan_settings(pilot)

    @pytest.mark.asyncio
    async def test_toggle_option_details(self, app):
        """
        Scenario: Toggling option details
            Given the plan settings screen is open
            When I toggle option details
            Then the details should be displayed
        """
        async with app.run_test() as pilot:
            await self._open_plan_window(pilot)
            self._assert_screen_is_plan_settings(pilot)

            destroy_block = pilot.app.screen.query_one("#destroy_block")
            clickable_icon = destroy_block.query_one(ClickableIcon)
            description = pilot.app.screen.query_one("#destroy_toggle")

            assert description.collapsed is True

            clickable_icon.scroll_visible()
            await click(pilot, clickable_icon)

            assert description.collapsed is False

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

        controls = pilot.app.query_one(TestPlanScreen.CONTROLS_ID)
        return controls.query_one(button_id)

    @staticmethod
    async def _open_plan_window(pilot):
        """
        Open the format window.
        Arguments:
            pilot (Pilot): The Pilot test instance.
        """
        header = pilot.app.query_one(TestPlanScreen.HEADER_ID)
        format_button = header.query_one(TestPlanScreen.PLAN_BUTTON_ID)
        format_button.scroll_visible()
        await click(pilot, format_button)

    @staticmethod
    def _assert_screen_is_plan_settings(pilot):
        """
        Assert that the current screen is the FormatSettingsScreen.
        Arguments:
            pilot (Pilot): The Pilot test instance.
        """
        assert isinstance(pilot.app.screen, PlanSettingsScreen)

    @staticmethod
    def _get_env_vars_container(container):
        """
        Retrieve the environment variables container.
        Arguments:
            pilot (Pilot): The Pilot test instance.
        Returns:
            Container: The environment variables container.
        """
        return container.query_one(f"#{TerraformPlanSettingsAttributes.ENV_VARS}")

    @staticmethod
    def _get_inline_vars_container(container):
        """
        Retrieve the inline variables container.
        Arguments:
            pilot (Pilot): The Pilot test instance.
        Returns:
            Container: The environment variables container.
        """
        return container.query_one(f"#{TerraformPlanSettingsAttributes.INLINE_VARS}")

    @staticmethod
    def _get_var_files_container(container):
        """
        Retrieve the variable files container.
        Arguments:
            pilot (Pilot): The Pilot test instance.
        Returns:
            Container: The environment variables container.
        """
        return container.query_one(f"#{TerraformPlanSettingsAttributes.VAR_FILES}")

    @staticmethod
    def get_add_key_value_button(container):
        return container.query_one(AddKeyValueButton)

    @staticmethod
    def get_add_file_button(container):
        return container.query_one(FileNavigatorModalButton)
