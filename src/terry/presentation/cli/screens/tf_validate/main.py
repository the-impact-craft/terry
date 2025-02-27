from textual import on
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll, Horizontal
from textual.widget import Widget
from textual.widgets import Static, Rule

from terry.domain.terraform.core.entities import TerraformValidateSettingsAttributes, ValidateSettings
from terry.presentation.cli.commands_descriptions import VALIDATE_DESCRIPTION, VALIDATE_NO_TESTS_DESCRIPTION
from terry.presentation.cli.messages.tf_validate_action_request import ValidateActionRequest
from terry.presentation.cli.widgets.buttons.open_file_navigator_modal_button import FileNavigatorModalButton
from terry.presentation.cli.widgets.form.checkbox_settings_block import CheckboxSettingBlock
from terry.presentation.cli.widgets.modal_control_label import ModalControlLabel
from terry.presentation.cli.screens.base.base_tf_settings_screen import BaseTfSettingsModalScreen
from terry.presentation.cli.screens.file_system_navigation.main import FileSystemSelectionValidationRule


class ValidateSettingsScreenControlLabel(ModalControlLabel):
    """A clickable label that emits an event when clicked."""


class ValidateSettingsScreen(BaseTfSettingsModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
    CONTAINER_ID: str = "validate_settings"
    CSS_PATH = "styles.tcss"

    def compose(self) -> ComposeResult:
        with Container(id=self.CONTAINER_ID):
            yield Static(VALIDATE_DESCRIPTION, id="about_validate")

            with VerticalScroll(id="settings"):
                yield Rule()

                yield CheckboxSettingBlock(
                    TerraformValidateSettingsAttributes.NO_TESTS,
                    "No tests",
                    VALIDATE_NO_TESTS_DESCRIPTION,
                )

                with Widget(id=TerraformValidateSettingsAttributes.TEST_DIRECTORY):
                    yield FileNavigatorModalButton(
                        content="+ Add Test Directory",
                        id="add_test_dir_button",
                        section_id=TerraformValidateSettingsAttributes.TEST_DIRECTORY,
                        validation_rules=[
                            FileSystemSelectionValidationRule(
                                action=lambda path: path.is_dir(), error_message="Selected path is not a directory"
                            )
                        ],
                    )
            yield Horizontal(
                ValidateSettingsScreenControlLabel("Close", name="close", id="close", classes="button"),
                ValidateSettingsScreenControlLabel("Apply", name="apply", id="apply", classes="button"),
                id="controls",
            )

    @on(ValidateSettingsScreenControlLabel.Close)
    async def close(self, _: ValidateSettingsScreenControlLabel.Close):
        self.app.pop_screen()

    @on(ValidateSettingsScreenControlLabel.Apply)
    async def apply(self, _: ValidateSettingsScreenControlLabel.Apply):
        result = self._initialize_result()

        result.update(self.process_checkbox_settings([TerraformValidateSettingsAttributes.NO_TESTS]))
        result.update(self.process_files([TerraformValidateSettingsAttributes.TEST_DIRECTORY]))

        if any(value is None for setting, value in result.items()):
            self.notify("Failed to process init settings", severity="error")
            return

        settings = ValidateSettings(**result)
        self.post_message(ValidateActionRequest(settings))  # pyright: ignore [reportArgumentType]
        self.app.pop_screen()

    def _initialize_result(self) -> dict:
        """Initialize the result dictionary with default values."""
        return {
            TerraformValidateSettingsAttributes.NO_TESTS: False,
            TerraformValidateSettingsAttributes.TEST_DIRECTORY: None,
        }
