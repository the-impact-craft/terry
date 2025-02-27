from dataclasses import dataclass
from pathlib import Path

from textual import events
from textual.message import Message
from textual.widgets import Static

from terry.presentation.cli.screens.file_system_navigation.main import FileSystemNavigationModal


class FileNavigatorModalButton(Static):
    """
    Represents a button that opens a modal for selecting variables file.

    This class extends the functionality of a Label component to provide a button
    that opens a modal for selecting a variables file when clicked. The button is
    designed to interact with user input and post messages indicating the selection
    of a variables file.
    """

    DEFAULT_CSS = """
    FileNavigatorModalButton {
        & :focus {
            color: $block-cursor-foreground;
            background: $block-cursor-background;
            text-style: $block-cursor-text-style;
        }
        margin_bottom: 1;
        margin_top: 1;
    }
    """

    def __init__(self, section_id, validation_rules=None, *args, **kwargs):
        if not section_id:
            raise ValueError("section_id cannot be empty")
        if "id" not in kwargs:
            raise ValueError("id is required")
        self.section_id = section_id
        self.validation_rules = validation_rules
        super().__init__(*args, **kwargs)

    @dataclass
    class Click(Message):
        """
        Represents a message indicating that the button was clicked.
        """

        button_id: str
        section_id: str
        file_path: Path

    can_focus = True

    def on_click(self, _: events.Click) -> None:
        self.on_select()

    def on_key(self, event: events.Key) -> None:
        """
        Handle the key event by logging the key and posting an ClickEvent.

        Args:
            event: The key event.
        """
        if event.key == "enter":
            self.on_select()

    def callback(self, file_path: Path) -> None:
        """
        Handles the callback event triggered by a file action.

        This method is responsible for processing the provided file path and
        triggering a post message action with the relevant details if the
        file path is valid.

        Args:
            file_path (Path): The path of the file associated with the callback event.

        Returns:
            None
        """
        if file_path:
            self.post_message(self.Click(button_id=self.id, section_id=self.section_id, file_path=file_path))  # type: ignore

    def on_select(self):
        """
        Calls the provided callback after a new screen is pushed. The new screen allows
        users to navigate the file system, applying specific validation rules for
        file or directory selection.

        Attributes:
            validation_rules (list): Rules to validate file or directory selections
                during navigation.
            callback (Callable): Function invoked after navigating to the new screen.

        """
        self.app.push_screen(FileSystemNavigationModal(validation_rules=self.validation_rules), callback=self.callback)  # type: ignore
