from dataclasses import dataclass

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Label

from terry.presentation.cli.widgets.modal_control_label import ModalControlLabel


class Control(ModalControlLabel):
    """
    A clickable label that emits an event when clicked.
    """

    @dataclass
    class Yes(Message):
        pass

    @dataclass
    class No(Message):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions_messages = {"yes": self.Yes, "no": self.No}


class QuestionScreen(ModalScreen[bool]):
    """Screen with a dialog to quit."""

    CSS_PATH = "styles.tcss"
    CONTAINER_ID = "question_screen"
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Pop screen"),
    ]

    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question

    def compose(self) -> ComposeResult:
        with Container(id=self.CONTAINER_ID):
            yield Label(self.question, classes="header")
            with Horizontal(id="controls"):
                yield Control("No", name="no", classes="button", id="no")
                yield Control("Yes", name="yes", classes="button", id="yes")

    def on_control_yes(self, _: Control.Yes) -> None:
        self.dismiss(True)

    def on_control_no(self, _: Control.No) -> None:
        self.dismiss(False)
