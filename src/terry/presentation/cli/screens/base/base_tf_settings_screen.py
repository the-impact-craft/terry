from typing import List

from textual import on
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets._toggle_button import ToggleButton
from terry.domain.operation_system.entities import Variable
from terry.presentation.cli.widgets.buttons.add_key_value_button import AddKeyValueButton
from terry.presentation.cli.widgets.buttons.open_file_navigator_modal_button import FileNavigatorModalButton
from terry.presentation.cli.widgets.form.file_selection_block import FileSelectionBlock
from terry.presentation.cli.widgets.form.key_value_block import KeyValueBlock
from terry.presentation.cli.widgets.form.text_input_block import TextInputBlock
from terry.presentation.cli.utils import get_unique_id


class BaseTfSettingsModalScreen(ModalScreen):
    """
    Represents a base class for handling settings modal screens.

    Provides utility functions to process different types of settings data, including
    checkbox settings, key-value settings, and environment variable file settings.
    Facilitates querying and updating settings based on user input in the UI.

    """

    def process_checkbox_settings(self, settings: list[str]) -> dict:
        """
        Processes checkbox settings and updates the result dictionary based on the settings list. Each setting corresponds to
        a checkbox, and the method checks for their existence to retrieve their states. If a checkbox is not found, its value
        in the result dictionary will be set to None.

        Args:
            settings (list[str]): A list of setting identifiers to query for checkbox states.
        Returns:
            dict: A dictionary containing the updated `result` with file contents for each setting.

        """
        result = {}
        for setting in settings:
            try:
                checkbox: ToggleButton = self.query_one(f"#{setting}")  # type: ignore
            except NoMatches:
                result[setting] = None
                return result
            result[setting] = checkbox.value
        return result

    def process_key_value_settings(self, settings: list[str]) -> dict:
        """
        Processes key-value settings and updates the result dictionary with the extracted values.

        This function iterates over the provided list of settings, extracts the corresponding key-value
        data blocks, and appends them to the result dictionary under the specified setting. If no values
        are found for a particular setting, an empty list is added to the result instead.

        Args:
            settings (list[str]): A list of strings representing the setting names for which key-value
                blocks need to be retrieved and processed.
        Returns:
            dict: A dictionary containing the updated `result` with file contents for each setting.

        """
        result = {}
        for setting in settings:
            values = self._extract_key_value_block_value(f"#{setting}")
            if values is None:
                result[setting] = None
                return result
            if setting not in result:
                result[setting] = []
            result[setting].extend(values)
        return result

    def process_files(self, settings: list[str]) -> dict:
        """
        Processes and extends the `result` dictionary with file contents based on provided
        `settings`. For each setting in the `settings` list, a query is performed to retrieve
        files associated with the respective setting. The content of the files is then appended
        to the corresponding entry in the `result` dictionary.

        Args:
            settings (list[str]): A list of settings for which associated file contents
                should be retrieved and appended to the `result` dictionary.

        Returns:
            dict: A dictionary containing the updated `result` with file contents for each setting.

        """
        result = {}
        for setting in settings:
            files = self.query(f"#{setting} > FileSelectionBlock").results()
            if setting not in result:
                result[setting] = []
            result[setting].extend(
                [file.content for file in files]  # type: ignore
            )
        return result

    def process_text_inputs(self, settings: list[str]) -> dict:
        """
        Processes a list of settings and retrieves the corresponding text input
        content for each setting. If a setting does not match any input, it returns
        None for that setting. The method ensures that only matched settings with
        valid text input are included in the result dictionary.

        Args:
            settings (list[str]): A list of strings representing the settings to
                query.

        Returns:
            dict: A dictionary where the keys are the provided settings and the
            values are the corresponding text input content or None if a setting
            does not match.
        """
        result = {}
        for setting in settings:
            try:
                text_input: TextInputBlock = self.query_one(f"#{setting}")  # type: ignore
            except NoMatches:
                result[setting] = None
                return result
            result[setting] = text_input.content or ""
        return result

    def _extract_key_value_block_value(self, selector: str) -> List[Variable] | None:
        result = []
        try:
            var_block = self.query_one(selector)
        except NoMatches:
            return

        try:
            env_vars = var_block.query(KeyValueBlock).results()
        except NoMatches:
            return []

        for env_var in env_vars:
            var_content = env_var.content
            if not var_content.key or not var_content.value:
                self.notify(f"Skip invalid inline variable {var_content.key} {var_content.value}", severity="warning")
                continue
            result.append(Variable(var_content.key, var_content.value))
        return result

    @on(AddKeyValueButton.Click)
    async def add_key_value_block(self, event: AddKeyValueButton.Click):
        try:
            container = self.query_one(f"#{event.section_id}")
        except NoMatches:
            return
        uuid = get_unique_id()
        await container.mount(KeyValueBlock(id=uuid, show_delete_button=True), before=f"#{event.id}")

    @on(FileNavigatorModalButton.Click)
    def add_file_block(self, event: FileNavigatorModalButton.Click):
        container = self.query_one(f"#{event.section_id}")
        uuid = get_unique_id()
        path = str(event.file_path.relative_to(self.app.work_dir))  # type: ignore

        # Todo: check if already added
        container.mount(FileSelectionBlock(id=uuid, path=path), before=f"#{event.button_id}")
