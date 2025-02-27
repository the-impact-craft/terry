from pathlib import Path
from time import time
from typing import Tuple

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import DirectoryTree, Tree
from textual.widgets._directory_tree import DirEntry

from terry.presentation.cli.messages.dir_activate_message import DirActivate
from terry.presentation.cli.messages.files_select_message import FileSelect
from terry.presentation.cli.messages.path_delete_message import PathDelete
from terry.presentation.cli.screens.question.main import QuestionScreen
from terry.settings import DOUBLE_CLICK_THRESHOLD


class TfDirectoryTree(DirectoryTree):
    """
    A directory tree for Terraform projects.
    """

    BINDINGS = Tree.BINDINGS + [
        Binding("backspace", "delete", "Select node"),
    ]

    def __init__(self, *args, **kwargs):
        """
        Initialize a TfDirectoryTree instance with tracking for file click events.

        This method sets up an initial state for tracking file clicks, allowing detection of double-click events.
        It initializes `last_file_click` with a timestamp slightly in the past and an empty directory entry to prevent
        immediate double-click detection.

        Parameters:
            *args: Variable positional arguments passed to the parent class initializer
            **kwargs: Variable keyword arguments passed to the parent class initializer

        Attributes:
            last_file_click (Tuple[float, DirEntry]): A tuple containing the timestamp of the last file click and the
            corresponding directory entry
            selected_path (Path): The path of the currently selected directory entry
        """
        self.last_file_click: Tuple[float, DirEntry] = (
            time() - 2,
            DirEntry(Path(), False),
        )
        self.selected_path: Path | None = None
        super().__init__(*args, **kwargs)

    def _on_tree_node_selected(self, event: Tree.NodeSelected[DirEntry]) -> None:
        """
        Handle the selection of a tree node with support for double-click detection.

        This method overrides the default tree node selection behavior to implement
        a double-click mechanism for file entries. It stops event propagation and
        checks for double-clicks within a 1.5-second window on the same file.

        Parameters:
            event (Tree.NodeSelected[DirEntry]): The tree node selection event containing
                the selected directory entry.

        Side Effects:
            - Stops the original event propagation
            - Updates the last file click tracking
            - Posts a FileSelect if a double-click is detected on a non-directory file

        Behavior:
            - Ignores selections with no associated directory entry
            - Tracks time and entry of the last file click
            - Detects double-clicks within 1.5 seconds on the same file
            - Triggers FileSelect for double-clicked files
            - Calls the parent class's node selection method
        """
        event.stop()
        dir_entry = event.node.data
        if dir_entry is None:
            return
        current_click = (time(), dir_entry)

        if not self._safe_is_dir(dir_entry.path):
            if (
                current_click[0] - self.last_file_click[0] < DOUBLE_CLICK_THRESHOLD
                and current_click[1] == self.last_file_click[1]
            ):
                self.post_message(FileSelect(dir_entry.path))
        else:
            self.post_message(DirActivate(dir_entry.path))

        self.last_file_click = current_click
        super()._on_tree_node_selected(event)

    def _on_tree_node_highlighted(self, event: Tree.NodeHighlighted[DirEntry]) -> None:
        """
        Handles the event triggered when a tree node is highlighted.

        This method processes the `Tree.NodeExpanded` event. It stops the event
        propagation, retrieves the data associated with the highlighted node,
        and updates the `selected_path` attribute with the node's path. If the
        node corresponds to a valid directory, it will post a `DirActivate`
        message to notify about the directory activation.

        Arguments:
            event (Tree.NodeHighlighted[DirEntry]): The event triggered when a tree node is highlighted
        """
        event.stop()
        entry = event.node.data
        if entry is None:
            return

        self.selected_path = entry.path
        if self._safe_is_dir(entry.path):
            self.post_message(DirActivate(entry.path))

    def action_delete(self):
        """
        Handle the delete action by posting a FileSelect message for the selected file.

        This method is called when the delete key is pressed while a file entry is selected in the directory tree.
        It posts a `FileSelect` message for the selected file to trigger the file selection action.

        Returns:
            None
        """
        if not self.selected_path:
            return

        def delete(accept: bool | None) -> None:
            """Called when QuitScreen is dismissed."""
            if accept and self.selected_path:
                self.post_message(PathDelete(path=self.selected_path, is_dir=self._safe_is_dir(self.selected_path)))

        self.app.push_screen(
            QuestionScreen(
                f"Delete path {self.selected_path.relative_to(self.path)}?",
            ),
            delete,
        )


class ProjectTree(VerticalScroll):
    update_date = reactive(None, recompose=True)

    DEFAULT_CSS = """
    ProjectTree > DirectoryTree {
        background: transparent;
    }

    """

    def __init__(self, work_dir: Path, *args, **kwargs):
        """
        Initialize a ProjectTree widget with a specified working directory.

        Parameters:
            work_dir (Path): The directory path to be used as the root for the project tree
            *args: Variable positional arguments to pass to the parent class initializer
            **kwargs: Variable keyword arguments to pass to the parent class initializer

        Attributes:
            work_dir (str): Stores the root directory path for the project tree
        """
        self.work_dir = work_dir
        self.work_dir_tree = None
        super().__init__(*args, **kwargs)

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
        Compose the project tree widget by yielding a Terraform-specific directory tree.

        This method creates and yields a `TfDirectoryTree` instance initialized with the specified working directory,
        which will be used to display the project's file structure.

        Returns:
            ComposeResult: A generator yielding the TfDirectoryTree widget for the project
        """
        self.work_dir_tree = TfDirectoryTree(self.work_dir)
        yield self.work_dir_tree

    def on_mount(self) -> None:
        """
        Set the border title of the project tree widget to "Project tree" when the widget is mounted.

        This method is called automatically when the widget is added to the application's widget tree,
        and it sets a descriptive title for the project tree container.

        Returns:
            None
        """
        self.border_title = "Project tree"
