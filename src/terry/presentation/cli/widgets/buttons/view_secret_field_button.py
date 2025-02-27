from dataclasses import dataclass

from textual import events
from textual.message import Message
from textual.widgets import Static


class ViewSecretFieldButton(Static):
    """
    Represents a button that views an environment variable block.

    This class extends the functionality of a static component to provide a button
    that views an environment variable block when clicked. The button is designed
    to interact with user input and post messages indicating the viewing of the
    associated environment variable block.
    """

    can_focus = True

    DEFAULT_CSS = """
    ViewSecretFieldButton {
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

        env_var_id: str

    def __init__(self, env_var_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.env_var_id = env_var_id

    def on_click(self, _: events.Click) -> None:
        self.post_message(self.Click(self.env_var_id))

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.post_message(self.Click(self.env_var_id))
