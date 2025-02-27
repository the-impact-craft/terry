from dataclasses import dataclass

from textual import events
from textual.message import Message
from textual.widgets import Static


class AddKeyValueButton(Static):
    """
    Represents a button for adding key-value pairs in a specific section.

    This class provides functionality for a UI button that allows a user to add
    a new environment variable block in a specific section. It can handle user
    actions such as clicks or key presses to trigger appropriate events.

    Attributes:
        DEFAULT_CSS (str): The default CSS style applied to the button, including
            focused state styles.
        can_focus (bool): Indicates whether the button can receive focus or not.
        section_id (str): The identifier for the section where this button is
            associated.
    """

    DEFAULT_CSS = """
        AddKeyValueButton {
            & :focus {
                color: $block-cursor-foreground;
                background: $block-cursor-background;
                text-style: $block-cursor-text-style;
            }
            margin_bottom: 1;
            margin_top: 1;
        }
        """

    can_focus = True

    def __init__(self, section_id, *args, **kwargs):
        if not section_id:
            raise ValueError("section_id cannot be empty")
        self.section_id = section_id
        super().__init__(*args, **kwargs)

    @dataclass
    class Click(Message):
        """
        Represents a message indicating that the button was clicked.
        """

        id: str
        section_id: str

    def on_click(self, event: events.Click) -> None:
        """
        Handles the click event on the button.

        This method is called when the button is clicked by the user. It posts a message
        indicating the addition of a new environment variable block, allowing further
        processing of the event.

        Arguments:
            event: An event representing the click action on the button.
        """

        self.trigger()

    def on_key(self, event: events.Key) -> None:
        """
        Handle the key event by logging the key and posting an ClickEvent.

        Args:
            event: The key event.
        """
        if event.key == "enter":
            self.trigger()

    def trigger(self):
        """
        Trigger the button by posting a click event.
        """
        self.post_message(self.Click(id=self.id, section_id=self.section_id))  # type: ignore
