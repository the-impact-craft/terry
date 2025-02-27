from textual import on, events
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll, Horizontal
from textual.widget import Widget
from textual.widgets import Static, Rule

from terry.domain.terraform.core.entities import TerraformInitSettingsAttributes, InitSettings
from terry.presentation.cli.commands_descriptions import (
    INIT_DESCRIPTION,
    INIT_DISABLE_BACKEND_DESCRIPTION,
    INIT_FORCE_COPY_DESCRIPTION,
    INIT_DISABLE_DOWNLOAD_DESCRIPTION,
    INIT_DISABLE_LOCK_DESCRIPTION,
    INIT_RECONFIGURE_DESCRIPTION,
    INIT_MIGRATE_STATE_DESCRIPTION,
    INIT_UPGRADE_DESCRIPTION,
    INIT_IGNORE_REMOTE_VERSION_DESCRIPTION,
    INIT_DISABLE_INPUT_DESCRIPTION,
    INIT_BACKEND_CONFIG_DESCRIPTION,
    INIT_PLUGIN_DIR_DESCRIPTION,
    INIT_TEST_DIRECTORY_DESCRIPTION,
)
from terry.presentation.cli.messages.tf_init_action_request import InitActionRequest
from terry.presentation.cli.widgets.buttons.add_key_value_button import AddKeyValueButton
from terry.presentation.cli.widgets.buttons.open_file_navigator_modal_button import FileNavigatorModalButton
from terry.presentation.cli.widgets.form.checkbox_settings_block import CheckboxSettingBlock
from terry.presentation.cli.widgets.form.collapsible_info_settings_block import CollapsibleInfoBlock
from terry.presentation.cli.widgets.modal_control_label import ModalControlLabel
from terry.presentation.cli.screens.base.base_tf_settings_screen import BaseTfSettingsModalScreen
from terry.presentation.cli.screens.file_system_navigation.main import FileSystemSelectionValidationRule


class InitSettingsScreenControlLabel(ModalControlLabel):
    """A clickable label that emits an event when clicked."""


class InitSettingsScreen(BaseTfSettingsModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
    CONTAINER_ID: str = "init_settings"
    CSS_PATH = "styles.tcss"

    def compose(self) -> ComposeResult:
        with Container(id=self.CONTAINER_ID):
            yield Static(INIT_DESCRIPTION, id="about_init")

            with VerticalScroll(id="settings"):
                yield Rule()

                yield CheckboxSettingBlock(
                    TerraformInitSettingsAttributes.DISABLE_BACKEND, "Disable backend", INIT_DISABLE_BACKEND_DESCRIPTION
                )
                yield CheckboxSettingBlock(
                    TerraformInitSettingsAttributes.FORCE_COPY,
                    "Suppress prompts about copying state",
                    INIT_FORCE_COPY_DESCRIPTION,
                )
                yield CheckboxSettingBlock(
                    TerraformInitSettingsAttributes.DISABLE_DOWNLOAD,
                    "Disable downloading modules",
                    INIT_DISABLE_DOWNLOAD_DESCRIPTION,
                )
                yield CheckboxSettingBlock(
                    TerraformInitSettingsAttributes.DISABLE_INPUT,
                    "Disable interactive prompts",
                    INIT_DISABLE_INPUT_DESCRIPTION,
                )
                yield CheckboxSettingBlock(
                    TerraformInitSettingsAttributes.DISABLE_HOLD_LOCK,
                    "Don't hold a state lock",
                    INIT_DISABLE_LOCK_DESCRIPTION,
                )
                yield CheckboxSettingBlock(
                    TerraformInitSettingsAttributes.RECONFIGURE, "Reconfigure the backend", INIT_RECONFIGURE_DESCRIPTION
                )
                yield CheckboxSettingBlock(
                    TerraformInitSettingsAttributes.MIGRATE_STATE,
                    "Reconfigure a backend and attempt to migrate state",
                    INIT_MIGRATE_STATE_DESCRIPTION,
                )
                yield CheckboxSettingBlock(
                    TerraformInitSettingsAttributes.UPGRADE,
                    "Install the latest module and provider versions",
                    INIT_UPGRADE_DESCRIPTION,
                )
                yield CheckboxSettingBlock(
                    TerraformInitSettingsAttributes.IGNORE_REMOTE_VERSION,
                    "Ignore remote version",
                    INIT_IGNORE_REMOTE_VERSION_DESCRIPTION,
                )

                yield Rule()
                yield CollapsibleInfoBlock(
                    "backend_config_description", "Backend configuration", INIT_BACKEND_CONFIG_DESCRIPTION
                )
                with Widget(id=TerraformInitSettingsAttributes.BACKEND_CONFIG):
                    yield AddKeyValueButton(
                        content="+ Add Config Variable",
                        section_id=TerraformInitSettingsAttributes.BACKEND_CONFIG,
                        id="add_config_value_button",
                    )
                with Widget(id=TerraformInitSettingsAttributes.BACKEND_CONFIG_PATH):
                    yield FileNavigatorModalButton(
                        content="+ Add Config File",
                        id="add_config_file_button",
                        section_id=TerraformInitSettingsAttributes.BACKEND_CONFIG_PATH,
                    )

                yield Rule()
                yield CollapsibleInfoBlock(
                    "plugin_dir_description",
                    "Plugin directory (Directory containing plugin binaries)",
                    INIT_PLUGIN_DIR_DESCRIPTION,
                )
                with Widget(id=TerraformInitSettingsAttributes.PLUGIN_DIRECTORY):
                    yield FileNavigatorModalButton(
                        content="+ Add Plugin Directory",
                        id="add_plugin_dir_button",
                        section_id=TerraformInitSettingsAttributes.PLUGIN_DIRECTORY,
                        validation_rules=[
                            FileSystemSelectionValidationRule(
                                action=lambda path: path.is_dir(), error_message="Selected path is not a directory"
                            )
                        ],
                    )

                yield Rule()
                yield CollapsibleInfoBlock("test_dir_description", "Test directory ", INIT_TEST_DIRECTORY_DESCRIPTION)
                with Widget(id=TerraformInitSettingsAttributes.TEST_DIRECTORY):
                    yield FileNavigatorModalButton(
                        content="+ Add Test Directory",
                        id="add_test_dir_button",
                        section_id=TerraformInitSettingsAttributes.TEST_DIRECTORY,
                        validation_rules=[
                            FileSystemSelectionValidationRule(
                                action=lambda path: path.is_dir(), error_message="Selected path is not a directory"
                            )
                        ],
                    )
            yield Horizontal(
                InitSettingsScreenControlLabel("Close", name="close", id="close", classes="button"),
                InitSettingsScreenControlLabel("Apply", name="apply", id="apply", classes="button"),
                id="controls",
            )

    def on_mount(self, _: events.Mount) -> None:
        self.query_one(f"#{self.CONTAINER_ID}").border_title = "Init Settings"

    @on(InitSettingsScreenControlLabel.Close)
    async def close(self, _: InitSettingsScreenControlLabel.Close):
        self.app.pop_screen()

    @on(InitSettingsScreenControlLabel.Apply)
    async def apply(self, _: InitSettingsScreenControlLabel.Apply):
        result = self._initialize_result()

        result.update(
            self.process_checkbox_settings(
                [
                    TerraformInitSettingsAttributes.DISABLE_BACKEND,
                    TerraformInitSettingsAttributes.FORCE_COPY,
                    TerraformInitSettingsAttributes.DISABLE_DOWNLOAD,
                    TerraformInitSettingsAttributes.DISABLE_INPUT,
                    TerraformInitSettingsAttributes.DISABLE_HOLD_LOCK,
                    TerraformInitSettingsAttributes.RECONFIGURE,
                    TerraformInitSettingsAttributes.MIGRATE_STATE,
                    TerraformInitSettingsAttributes.UPGRADE,
                    TerraformInitSettingsAttributes.IGNORE_REMOTE_VERSION,
                ],
            )
        )

        result.update(
            self.process_key_value_settings(
                [
                    TerraformInitSettingsAttributes.BACKEND_CONFIG,
                ],
            )
        )

        result.update(
            self.process_files(
                [
                    TerraformInitSettingsAttributes.BACKEND_CONFIG_PATH,
                    TerraformInitSettingsAttributes.PLUGIN_DIRECTORY,
                    TerraformInitSettingsAttributes.TEST_DIRECTORY,
                ]
            )
        )
        if any(value is None for setting, value in result.items()):
            self.notify("Failed to process init settings", severity="error")
            return

        settings = InitSettings(**result)
        self.post_message(InitActionRequest(settings))  # pyright: ignore [reportArgumentType]
        self.app.pop_screen()

    def _initialize_result(self) -> dict:
        """Initialize the result dictionary with default values."""
        return {
            TerraformInitSettingsAttributes.DISABLE_BACKEND: False,
            TerraformInitSettingsAttributes.BACKEND_CONFIG: {},
            TerraformInitSettingsAttributes.BACKEND_CONFIG_PATH: None,
            TerraformInitSettingsAttributes.FORCE_COPY: False,
            TerraformInitSettingsAttributes.DISABLE_DOWNLOAD: False,
            TerraformInitSettingsAttributes.DISABLE_INPUT: False,
            TerraformInitSettingsAttributes.DISABLE_HOLD_LOCK: False,
            TerraformInitSettingsAttributes.PLUGIN_DIRECTORY: None,
            TerraformInitSettingsAttributes.RECONFIGURE: False,
            TerraformInitSettingsAttributes.MIGRATE_STATE: False,
            TerraformInitSettingsAttributes.UPGRADE: False,
            TerraformInitSettingsAttributes.IGNORE_REMOTE_VERSION: False,
            TerraformInitSettingsAttributes.TEST_DIRECTORY: None,
        }
