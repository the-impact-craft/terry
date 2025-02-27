from dataclasses import dataclass

from textual import events
from textual.message import Message
from textual.widgets import Static


class DeleteButton(Static):
    """
    Represents a specialized button used for deletion purposes.

    The DeleteButton is designed with specific styling and functionality to handle
    deletion actions within a graphical user interface. This button supports keyboard
    interactions and can respond to user clicks, emitting a message indicating the action
    for further processing.

    Attributes:
        can_focus (bool): Indicates if the button can receive focus. Defaults to True.
        DEFAULT_CSS (str): The default CSS styling applied to the button, including
            focus-based styling.
    """

    can_focus = True

    DEFAULT_CSS = """
    DeleteButton {
        &:focus {
            color:$block-cursor-background;
            text-style: $block-cursor-text-style;
        }
    }
    """

    @dataclass
    class Click(Message):
        """
        Represents a message indicating that the button was clicked.
        """

        component_id: str

    def __init__(self, component_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.component_id = component_id

    def on_click(self, event: events.Click) -> None:
        """
        Handles the click event on the button.

        This method is called when the button is clicked by the user. It posts a message
        indicating the deletion of the associated environment variable block, allowing
        further processing of the event.
        """
        self.post_message(self.Click(self.component_id))

    def on_key(self, event: events.Key) -> None:
        if event.key == "backspace":
            self.post_message(self.Click(self.component_id))
