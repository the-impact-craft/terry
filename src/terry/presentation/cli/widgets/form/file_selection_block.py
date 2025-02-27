from pathlib import Path

from textual import events, on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

from terry.presentation.cli.widgets.buttons.delete_button import DeleteButton


class FileSelectionBlock(Horizontal):
    """
    FileSelectionBlock is a UI component for managing file selections.

    This class provides a grid-based UI layout for managing file selections with
    associated functionality, such as file display and deletion. It is built
    on the Horizontal layout class and enforces unique identifiers for proper
    handling of UI elements. The component uses a two-column grid layout
    structured to display a static file path on the left and a delete button
    on the right.

    Attributes:
        DEFAULT_CSS (str): Default CSS styles for the component, defining layout
            properties such as width, height, padding, and alignment, as well
            as child element positioning.
        path (str): The file path associated with the file selection block.
    """

    DEFAULT_CSS = """
    FileSelectionBlock {
        width: 100%;
        height: auto;
        padding: 0 0 0 0;
        layout: grid;
        grid-size: 2 1;

        & > Static {
            padding: 0 1;
            width: 100%;
            content-align: left top;
        }

        & > DeleteButton {
            padding: 0 1;
            width: 100%;
            content-align: right top;
        }
    }
    """

    def __init__(self, path: str | Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "id" not in kwargs:
            raise ValueError("id is required")
        self.path = path

    @property
    def content(self) -> str | Path:
        return self.path

    def on_mount(self, event: events.Mount) -> None:
        self.focus()

    def compose(self) -> ComposeResult:
        yield Static(f"{self.path}")
        yield DeleteButton(content="x", component_id=self.id)

    @on(DeleteButton.Click)
    def delete_file_block(self, event: DeleteButton.Click):
        if event.component_id == self.id:
            self.remove()
