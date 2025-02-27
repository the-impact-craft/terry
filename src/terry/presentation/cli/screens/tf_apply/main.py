from textual import on, events
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll, Horizontal
from textual.widget import Widget
from textual.widgets import Static, Rule

from terry.domain.terraform.core.entities import TerraformApplySettingsAttributes, ApplySettings
from terry.presentation.cli.commands_descriptions import (
    APPLY_DESCRIPTION,
    APPLY_AUTO_APPROVE_DESCRIPTION,
    APPLY_DESTROY_DESCRIPTION,
    APPLY_INPUT_DESCRIPTION,
    APPLY_DISABLE_BACKUP_DESCRIPTION,
    APPLY_BACKUP_DESCRIPTION,
    APPLY_STATE_OUT_DESCRIPTION,
    APPLY_STATE_DESCRIPTION,
    APPLY_DISABLE_LOCK_DESCRIPTION,
    APPLY_PLAN_DESCRIPTION,
)
from terry.presentation.cli.messages.tf_apply_action_request import ApplyActionRequest
from terry.presentation.cli.widgets.buttons.open_file_navigator_modal_button import FileNavigatorModalButton
from terry.presentation.cli.widgets.form.checkbox_settings_block import CheckboxSettingBlock
from terry.presentation.cli.widgets.form.collapsible_info_settings_block import CollapsibleInfoBlock
from terry.presentation.cli.widgets.form.text_input_block import TextInputBlock
from terry.presentation.cli.widgets.modal_control_label import ModalControlLabel
from terry.presentation.cli.screens.base.base_tf_settings_screen import BaseTfSettingsModalScreen
from terry.presentation.cli.screens.file_system_navigation.main import FileSystemSelectionValidationRule


class ApplySettingsScreenControlLabel(ModalControlLabel):
    """A clickable label that emits an event when clicked."""


class ApplySettingsScreen(BaseTfSettingsModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
    CONTAINER_ID: str = "apply_settings"
    CSS_PATH = "styles.tcss"

    def compose(self) -> ComposeResult:
        with Container(id=self.CONTAINER_ID):
            yield Static(APPLY_DESCRIPTION, id="about_apply")

            with VerticalScroll(id="settings"):
                yield Rule()

                yield CheckboxSettingBlock(
                    TerraformApplySettingsAttributes.AUTO_APPROVE, "Auto approve", APPLY_AUTO_APPROVE_DESCRIPTION
                )

                yield CheckboxSettingBlock(
                    TerraformApplySettingsAttributes.DESTROY, "Destroy", APPLY_DESTROY_DESCRIPTION
                )

                yield CheckboxSettingBlock(
                    TerraformApplySettingsAttributes.DISABLE_BACKUP, "Disable backup", APPLY_DISABLE_BACKUP_DESCRIPTION
                )

                yield CheckboxSettingBlock(
                    TerraformApplySettingsAttributes.DISABLE_LOCK, "Disable lock", APPLY_DISABLE_LOCK_DESCRIPTION
                )

                yield CheckboxSettingBlock(
                    TerraformApplySettingsAttributes.INPUT, "Ask for input for variables", APPLY_INPUT_DESCRIPTION
                )

                yield Rule()
                yield TextInputBlock(
                    TerraformApplySettingsAttributes.BACKUP,
                    "Backup path",
                    APPLY_BACKUP_DESCRIPTION,
                    id=TerraformApplySettingsAttributes.BACKUP,
                )
                yield TextInputBlock(
                    TerraformApplySettingsAttributes.STATE_OUT,
                    "State out path",
                    APPLY_STATE_OUT_DESCRIPTION,
                    id=TerraformApplySettingsAttributes.STATE_OUT,
                )

                yield Rule()
                yield CollapsibleInfoBlock("state", "State path", APPLY_STATE_DESCRIPTION)
                with Widget(id=TerraformApplySettingsAttributes.STATE):
                    yield FileNavigatorModalButton(
                        content="+ State file path",
                        id="add_state_path",
                        section_id=TerraformApplySettingsAttributes.STATE,
                        validation_rules=[
                            FileSystemSelectionValidationRule(
                                action=lambda path: path.is_file(), error_message="Selected path is not a file"
                            )
                        ],
                    )

                yield Rule()
                yield CollapsibleInfoBlock("plan", "Plan path", APPLY_PLAN_DESCRIPTION)
                with Widget(id=TerraformApplySettingsAttributes.PLAN):
                    yield FileNavigatorModalButton(
                        content="+ Plan file path",
                        id="add_plan_path",
                        section_id=TerraformApplySettingsAttributes.PLAN,
                        validation_rules=[
                            FileSystemSelectionValidationRule(
                                action=lambda path: path.is_file(), error_message="Selected path is not a file"
                            )
                        ],
                    )

            yield Horizontal(
                ApplySettingsScreenControlLabel("Close", name="close", id="close", classes="button"),
                ApplySettingsScreenControlLabel("Apply", name="apply", id="apply", classes="button"),
                id="controls",
            )

    def on_mount(self, _: events.Mount) -> None:
        self.query_one(f"#{self.CONTAINER_ID}").border_title = "Apply Settings"

    @on(ApplySettingsScreenControlLabel.Close)
    def on_close(self, _: ApplySettingsScreenControlLabel.Close):
        self.dismiss(None)

    @on(ApplySettingsScreenControlLabel.Apply)
    def on_apply(self, _: ApplySettingsScreenControlLabel.Apply):
        result = self._initialize_result()

        checkbox_settings = self.process_checkbox_settings(
            [
                TerraformApplySettingsAttributes.AUTO_APPROVE,
                TerraformApplySettingsAttributes.DESTROY,
                TerraformApplySettingsAttributes.DISABLE_BACKUP,
                TerraformApplySettingsAttributes.DISABLE_LOCK,
                TerraformApplySettingsAttributes.INPUT,
            ],
        )

        paths_settings = self.process_files(
            [
                TerraformApplySettingsAttributes.STATE,
                TerraformApplySettingsAttributes.PLAN,
            ]
        )

        text_input_settings = self.process_text_inputs(
            [
                TerraformApplySettingsAttributes.BACKUP,
                TerraformApplySettingsAttributes.STATE_OUT,
            ]
        )

        result.update({**checkbox_settings, **paths_settings, **text_input_settings})

        failed_settings = [setting for setting, value in result.items() if value is None]
        if failed_settings:
            self.notify(f"Failed to process settings: {', '.join(failed_settings)}", severity="error")
            return

        settings = ApplySettings(**result)
        self.post_message(ApplyActionRequest(settings))  # pyright: ignore [reportArgumentType]
        self.app.pop_screen()

    def _initialize_result(self) -> dict:
        """Initialize the result dictionary with default values."""
        return {
            TerraformApplySettingsAttributes.AUTO_APPROVE: None,
            TerraformApplySettingsAttributes.DESTROY: None,
            TerraformApplySettingsAttributes.DISABLE_BACKUP: None,
            TerraformApplySettingsAttributes.DISABLE_LOCK: None,
            TerraformApplySettingsAttributes.INPUT: None,
            TerraformApplySettingsAttributes.BACKUP: None,
            TerraformApplySettingsAttributes.STATE: None,
            TerraformApplySettingsAttributes.STATE_OUT: None,
        }
