from dataclasses import dataclass

from textual import events
from textual.message import Message
from textual.widgets import Label


class ModalControlLabel(Label):
    """A clickable label that emits an event when clicked."""

    DEFAULT_CSS = """
    ModalControlLabel {
        margin: 0 4;
        padding: 0 0;
        width: auto;
        min-width: 16;
        height: auto;
        color: white;
        background: $surface;
        border: solid $surface-lighten-1;
        text-align: center;
        content-align: center middle;
        text-style: bold;

        &:disabled {
            text-opacity: 0.6;
        }

        &:focus {
            background-tint: $foreground 5%;
        }
        &:hover {
            border-top: solid $surface;
            background: $surface-darken-1;
        }
        &.-active {
            background: $surface;
            border-bottom: solid $surface-darken-1;
            tint: $background 30%;
        }
    }
    """
    can_focus = True

    @dataclass
    class Close(Message):
        """
        Posted when the close button is clicked.

        Can be handled using `on_cancel`.
        """

        pass

    @dataclass
    class Apply(Message):
        """
        Posted when the apply button is clicked.

        Can be handled using `on_apply`.
        """

        pass

    def __init__(self, *args, **kwargs):
        """
        Initialize a ClickableLabel widget.

        Parameters:
            *args: Variable length argument list passed to the parent class constructor.
            **kwargs: Arbitrary keyword arguments passed to the parent class constructor.
        """
        super().__init__(*args, **kwargs)

        self.actions_messages = {"close": self.Close, "apply": self.Apply}

    def on_click(self, _: events.Click) -> None:
        """
        Handle the click event by logging the click and posting an ClickEvent.

        Args:
            _: The click event.
        """
        self.on_action_click()

    def on_key(self, event: events.Key) -> None:
        """
        Handle key events for the label.

        Args:
            event: The key event.
        """
        if event.key == "enter":
            self.on_action_click()

    def on_action_click(self):
        """
        Handle the action click event by posting the corresponding message.
        """
        if not self.name:
            self.notify("No action name was provided", severity="warning")
            return
        message_class = self.actions_messages.get(self.name)
        if not message_class:
            self.notify("Unknown action was triggered", severity="warning")
            return
        self.post_message(message_class())  # type: ignore
