from dataclasses import dataclass

from textual import events
from textual.message import Message
from textual.widgets import Label


class ClickableTfActionLabel(Label):
    """A clickable label that emits an event when clicked."""

    can_focus = True
    UNKNOWN_ACTION_MESSAGE = "Unknown action was triggered"

    @dataclass
    class ClickEvent(Message):
        action: str

    def __init__(self, *args, **kwargs):
        """
        Initialize a ClickableLabel widget.

        Parameters:
            *args: Variable length argument list passed to the parent class constructor.
            **kwargs: Arbitrary keyword arguments passed to the parent class constructor.
        """
        super().__init__(*args, **kwargs)
        if "name" not in kwargs:
            raise ValueError("name is required")

    def on_click(self, _: events.Click) -> None:
        """
        Handle the click event by logging the click and posting an ClickEvent.

        Args:
            _: The click event.
        """
        if not self.name:
            self.notify(self.UNKNOWN_ACTION_MESSAGE, severity="warning")
            return
        self.post_message(self.ClickEvent(self.name))

    def on_key(self, event: events.Key) -> None:
        """
        Handle the key event by logging the key and posting an ClickEvent.

        Args:
            event: The key event.
        """
        if event.key == "enter":
            if not self.name:
                self.notify(self.UNKNOWN_ACTION_MESSAGE, severity="warning")
                return
            self.post_message(self.ClickEvent(self.name))
