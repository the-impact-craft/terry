from textual import events, on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets import Label, RadioSet, RadioButton

from terry.domain.terraform.core.entities import FormatScope
from terry.presentation.cli.messages.tf_format_action_request import FormatActionRequest
from terry.presentation.cli.widgets.modal_control_label import (
    ModalControlLabel,
)


class FormatModalControlLabel(ModalControlLabel):
    """A clickable label that emits an event when clicked."""


class FormatSettingsScreen(ModalScreen):
    CONTAINER_ID = "format_settings"
    CSS_PATH = "styles.tcss"
    BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def __init__(self):
        super().__init__()
        self.format_scopes = [
            FormatScope("Apply to current file", "crtl+t+f", True, "current_file"),
            FormatScope("Apply to all project", "crtl+t+f+a", False, "all_project"),
        ]

    def compose(self) -> ComposeResult:
        """
        Generates the layout and content of the modal user interface for selecting the scope
        of formatting. The composed UI features a container housing a label, a set of radio
        buttons to choose between various formatting scopes, and action buttons for closing
        or applying the modal dialog.
        """
        with Container(id=self.CONTAINER_ID):
            yield Label("Select the scope of the formatting:")
            with RadioSet(id="format_scope_selector"):
                for scope in self.format_scopes:
                    yield RadioButton(label=f"{scope.label} | {scope.shortcut}", value=scope.active)
            yield Horizontal(
                FormatModalControlLabel("Close", name="close", classes="button", id="close"),
                FormatModalControlLabel("Apply", name="apply", classes="button", id="apply"),
                id="controls",
            )

    def on_mount(self, event: events.Mount) -> None:
        """
        Handles the operations to be performed when the component is mounted to the screen.

        Arguments:
            event: An event associated with the mounting process, containing relevant
                information and references required for the operation.
        """
        self.query_one(f"#{self.CONTAINER_ID}").border_title = "Format Settings"

    def apply(self, format: FormatScope) -> None:
        self.post_message(FormatActionRequest(format=format))

    def apply_format_settings(self) -> None:
        """
        Apply formatting settings based on the selected scope.

        This method handles the process of applying a format setting selected
        by the user from a UI component, ensuring the selected format scope
        exists and is valid. It performs validation checks on the selection and
        notifies the user of any errors. If the selection is valid, a formatted
        message is sent and the current UI screen is closed.

        If the selection is not valid, an error notification is raised instead
        of proceeding with the operations.

        """
        try:
            radio_set = self.query_one("#format_scope_selector")
        except NoMatches:
            self.notify("Error", severity="error")
            return

        selected_index = radio_set._selected  # type: ignore

        if selected_index >= len(self.format_scopes):
            self.notify("Error", severity="error")
            return
        format_scope = self.format_scopes[selected_index]
        self.apply(format_scope)
        self.app.pop_screen()

    @on(FormatModalControlLabel.Close)
    def on_cancel(self, _: FormatModalControlLabel.Close) -> None:
        """
        Handles the action triggered when the cancel event is invoked through the FormatModalControlLabel
        of type Close. This method ensures that the current screen is appropriately removed from the
        screen stack of the application when the cancel event is processed.

        Arguments:
            _: The FormatModalControlLabel event of type Close.
        """
        self.app.pop_screen()

    @on(FormatModalControlLabel.Apply)
    def on_apply(self, _: FormatModalControlLabel.Apply) -> None:
        """
        Handles the application of format settings when the Apply action is triggered.

        This method is invoked when the `Apply` action associated with
        `FormatModalControlLabel` is called. It ensures that the format settings
        are applied correctly.

        Arguments:
            _: The FormatModalControlLabel event of type Apply.
        """
        self.apply_format_settings()
