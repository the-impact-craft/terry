from dataclasses import dataclass

from textual import events
from textual.message import Message
from textual.widgets import Static


class ClickableIcon(Static):
    """
    Represents a clickable icon within the interface.

    This class is a specialization of the Static component, designed to handle click
    events and post messages indicating which icon was clicked. The ClickableIcon
    interacts with user input to provide a dynamic and interactive experience
    in the application.
    """

    def __init__(self, *args, **kwargs):
        if "name" not in kwargs:
            raise ValueError("'name' parameter is required for ClickableIcon")
        if not isinstance(kwargs["name"], str):
            raise ValueError("'name' parameter must be a string")
        super().__init__(*args, **kwargs)

    @dataclass
    class Click(Message):
        """
        Represents a message indicating that the icon was clicked.

        This class encapsulates data regarding the click event on the icon. It is used
        for transmitting and processing information about the user interaction with the
        clickable icon. The purpose of this class is to provide a structured format for
        handling click events on the icon.

        Arguments:
            name: str
        """

        name: str

    def on_click(self, event: events.Click) -> None:
        """
        Handles the click event on the icon.

        This method is called when the icon is clicked by the user. It posts a message
        indicating which icon was clicked, allowing further processing of the event.

        Arguments:
            event: An event representing the click action on the icon.
        """
        if not self.name:
            self.notify("Unknown action", severity="error")
            return
        self.post_message(self.Click(self.name))
