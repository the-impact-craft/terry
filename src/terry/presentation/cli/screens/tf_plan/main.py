from pathlib import Path
from typing import List

from textual import on, events
from textual.app import ComposeResult
from textual.containers import VerticalScroll, Container, Horizontal
from textual.widget import Widget
from textual.widgets import Static, Rule

from terry.domain.operation_system.entities import Variable
from terry.domain.terraform.core.entities import PlanSettings, TerraformPlanSettingsAttributes
from terry.presentation.cli.commands_descriptions import (
    PLAN_ABOUT_DESCRIPTION,
    PLAN_DESTROY_DESCRIPTION,
    PLAN_REFRESH_ONLY_DESCRIPTION,
    PLAN_MODE_SETTINGS_DESCRIPTION,
    PLAN_INLINE_VAR_DESCRIPTION,
    PLAN_ENV_VAR_DESCRIPTION,
    PLAN_VAR_FILE_DESCRIPTION,
    PLAN_REFRESH_FALSE,
    PLAN_OUT_DESCRIPTION,
)
from terry.presentation.cli.messages.tf_plan_action_request import PlanActionRequest
from terry.presentation.cli.widgets.buttons.add_key_value_button import AddKeyValueButton
from terry.presentation.cli.widgets.buttons.open_file_navigator_modal_button import FileNavigatorModalButton
from terry.presentation.cli.widgets.form.checkbox_settings_block import CheckboxSettingBlock
from terry.presentation.cli.widgets.form.collapsible_info_settings_block import CollapsibleInfoBlock
from terry.presentation.cli.widgets.form.key_value_block import KeyValueBlock
from terry.presentation.cli.widgets.form.text_input_block import TextInputBlock
from terry.presentation.cli.widgets.modal_control_label import ModalControlLabel
from terry.presentation.cli.screens.base.base_tf_settings_screen import BaseTfSettingsModalScreen
from terry.presentation.cli.screens.file_system_navigation.main import FileSystemSelectionValidationRule
from terry.presentation.cli.utils import get_unique_id


class PlanSettingsScreenControlLabel(ModalControlLabel):
    """A clickable label that emits an event when clicked."""


class PlanSettingsScreen(BaseTfSettingsModalScreen):
    """
    Represents the screen for configuring plan settings.

    This class defines the layout and functionality of the screen for configuring
    plan settings in the application. It provides a user interface for setting
    various options related to the Terraform plan command, such as destroy mode,
    refresh only mode, and environment variables. The screen allows users to interact
    with the settings and provides visual feedback for the selected options.
    """

    CONTAINER_ID: str = "plan_settings"
    CSS_PATH = Path("styles.tcss")
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def __init__(self, env_vars: List[Variable] | None = None, *args, **kwargs):
        self.env_vars = env_vars or []
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with Container(id=self.CONTAINER_ID):
            yield Static(PLAN_ABOUT_DESCRIPTION, id="about_plan")

            with VerticalScroll(id="settings"):
                yield Rule()
                yield CollapsibleInfoBlock(
                    "mode_settings",
                    "Mode Settings:",
                    PLAN_MODE_SETTINGS_DESCRIPTION,
                )
                yield CheckboxSettingBlock(TerraformPlanSettingsAttributes.DESTROY, "Destroy", PLAN_DESTROY_DESCRIPTION)
                yield CheckboxSettingBlock(
                    TerraformPlanSettingsAttributes.REFRESH_ONLY, "Refresh only", PLAN_REFRESH_ONLY_DESCRIPTION
                )
                yield CheckboxSettingBlock(TerraformPlanSettingsAttributes.NO_REFRESH, "No refresh", PLAN_REFRESH_FALSE)

                yield Rule()
                yield TextInputBlock(
                    TerraformPlanSettingsAttributes.OUT,
                    "Plan out path",
                    PLAN_OUT_DESCRIPTION,
                    id=TerraformPlanSettingsAttributes.OUT,
                )

                yield Rule()
                yield CollapsibleInfoBlock(
                    "env_vars",
                    "Environment variables:",
                    PLAN_ENV_VAR_DESCRIPTION,
                )
                with Widget(id=TerraformPlanSettingsAttributes.ENV_VARS):
                    for env_var in self.env_vars:
                        uuid = get_unique_id()
                        yield KeyValueBlock(
                            key=env_var.name,
                            value=env_var.value,
                            id=uuid,
                            show_view_button=True,
                            is_password=True,
                        )

                    yield AddKeyValueButton(
                        content="+ Add Environment Variable",
                        section_id=TerraformPlanSettingsAttributes.ENV_VARS,
                        id="add_env_var_button",
                    )

                yield Rule()
                yield CollapsibleInfoBlock(
                    "inline_variables",
                    "Inline variables:",
                    PLAN_INLINE_VAR_DESCRIPTION,
                )
                with Widget(id=TerraformPlanSettingsAttributes.INLINE_VARS):
                    yield AddKeyValueButton(
                        content="+ Add Inline Variable", section_id="inline_vars", id="add_inline_var_button"
                    )

                yield Rule()
                yield CollapsibleInfoBlock(
                    "var_files",
                    "Variables Files:",
                    PLAN_VAR_FILE_DESCRIPTION,
                )
                with Widget(id=TerraformPlanSettingsAttributes.VAR_FILES):
                    yield FileNavigatorModalButton(
                        content="+ Add Variables File",
                        id="add_var_file_button",
                        section_id=TerraformPlanSettingsAttributes.VAR_FILES,
                        validation_rules=[
                            FileSystemSelectionValidationRule(
                                action=lambda path: path.is_file(), error_message="Selected path is not a file"
                            )
                        ],
                    )
            yield Horizontal(
                PlanSettingsScreenControlLabel("Close", name="close", id="close", classes="button"),
                PlanSettingsScreenControlLabel("Apply", name="apply", id="apply", classes="button"),
                id="controls",
            )

    def on_mount(self, _: events.Mount) -> None:
        self.query_one(f"#{self.CONTAINER_ID}").border_title = "Plan Settings"

    @on(PlanSettingsScreenControlLabel.Close)
    def on_close(self, _: PlanSettingsScreenControlLabel.Close):
        self.dismiss(None)

    @on(PlanSettingsScreenControlLabel.Apply)
    def on_apply(self, _: PlanSettingsScreenControlLabel.Apply):
        result = self._initialize_result()

        checkbox_settings = self.process_checkbox_settings(
            [
                TerraformPlanSettingsAttributes.DESTROY,
                TerraformPlanSettingsAttributes.REFRESH_ONLY,
                TerraformPlanSettingsAttributes.NO_REFRESH,
            ],
        )

        key_value_settings = self.process_key_value_settings(
            [
                TerraformPlanSettingsAttributes.ENV_VARS,
                TerraformPlanSettingsAttributes.INLINE_VARS,
            ],
        )

        text_input_settings = self.process_text_inputs(
            [
                TerraformPlanSettingsAttributes.OUT,
            ]
        )

        file_settings = self.process_files([TerraformPlanSettingsAttributes.VAR_FILES])

        result.update({**checkbox_settings, **key_value_settings, **file_settings, **text_input_settings})

        if any(value is None for setting, value in result.items()):
            self.notify("Failed to process plan settings", severity="error")
            return

        settings = PlanSettings(**result)
        self.post_message(PlanActionRequest(settings))  # pyright: ignore [reportArgumentType]
        self.app.pop_screen()

    def _initialize_result(self) -> dict:
        """Initialize the result dictionary with default values."""
        return {
            TerraformPlanSettingsAttributes.DESTROY: None,
            TerraformPlanSettingsAttributes.REFRESH_ONLY: None,
            TerraformPlanSettingsAttributes.NO_REFRESH: None,
            TerraformPlanSettingsAttributes.ENV_VARS: [],
            TerraformPlanSettingsAttributes.INLINE_VARS: [],
            TerraformPlanSettingsAttributes.VAR_FILES: [],
            TerraformPlanSettingsAttributes.OUT: None,
        }
