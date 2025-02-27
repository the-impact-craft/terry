from time import time
from typing import Tuple

from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label, ListView, ListItem

from terry.presentation.cli.messages.files_select_message import FileSelect


class LabelItem(ListItem):
    def __init__(self, label: str) -> None:
        """
        Initialize a label item with the specified text.

        Parameters:
            label (str): The text to be displayed for this list item.
        """
        super().__init__()
        self.label = label

    def compose(self) -> ComposeResult:
        """
        Compose the visual representation of a label item.

        Returns:
            ComposeResult: A generator yielding a Label widget with the predefined label text.
        """
        yield Label(self.label)


class StateFiles(VerticalScroll):
    """
    Widget for managing the state files.
    """

    DEFAULT_CSS = """
    StateFiles > ListView {
        background: transparent;
    }
    """
    STATE_FILES_LIST_COMPONENT_ID = "state_files_list"

    def __init__(self, state_files, *args, **kwargs):
        """
        Initialize a StateFiles widget with a list of state files.

        Parameters:
            state_files (List[str]): A list of state file names to be displayed in the widget.
            *args: Variable length argument list passed to the parent class constructor.
            **kwargs: Arbitrary keyword arguments passed to the parent class constructor.

        Attributes:
            state_files (List[str]): Stores the list of state files for the widget.
            last_file_click (Tuple[float, str]): Tracks the timestamp and label of the last file click,
                initialized with a timestamp two seconds in the past and an empty label to prevent
                immediate double-click detection.
        """
        super().__init__(*args, **kwargs)
        self.state_files = state_files
        self.last_file_click: Tuple[float, str] = (
            time() - 2,
            "",
        )

    @property
    def can_focus(self) -> bool:
        """
        Indicates whether the widget can receive focus through keyboard navigation.

        Returns:
            bool: Always returns False, preventing the widget from being focused via tabbing.
        """
        return False

    def compose(self) -> ComposeResult:
        """
        Compose the state files list view with label items.

        Yields a ListView populated with LabelItem instances for each state file in the component.

        Returns:
            ComposeResult: A ListView containing LabelItem widgets representing state files,
            with a predefined component ID.
        """
        yield ListView(
            *[LabelItem(state_file) for state_file in self.state_files],
            id=self.STATE_FILES_LIST_COMPONENT_ID,
        )

    def on_mount(self) -> None:
        """
        Set the border title of the widget to "State files" when the widget is mounted.

        This method is called automatically by the Textual framework when the widget is first mounted
        to the application, and sets a descriptive title for the widget's border.
        """
        self.border_title = "State files"

    @on(ListView.Selected)
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """
        Handle selection events in the state files list view, detecting double-click interactions.

        This method is triggered when an item in the list view is selected. It checks if the selected item is from the
        state files list and implements a double-click detection mechanism by comparing the time and label of
        consecutive clicks.

        Parameters:
            event (ListView.Selected): The selection event containing details about the selected list item.

        Side Effects:
            - Updates `self.last_file_click` with the current click's timestamp and label.
            - Posts a `FileSelect` if a double-click is detected within 1.5 seconds on the same item.

        Behavior:
            - Verifies the selection is from the state files list component.
            - Detects double-clicks by checking:
                1. Time between clicks is less than 1.5 seconds
                2. The same list item is clicked twice
            - Triggers a file double-click event when conditions are met.
        """
        label = event.item.label  # type: ignore
        if event.list_view.id == self.STATE_FILES_LIST_COMPONENT_ID:
            current_click = (time(), label)
            if current_click[0] - self.last_file_click[0] < 1.5 and current_click[1] == self.last_file_click[1]:
                self.post_message(FileSelect(label))
            self.last_file_click = current_click
