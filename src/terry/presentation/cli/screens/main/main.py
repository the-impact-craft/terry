import atexit
from pathlib import Path
from typing import List

from dependency_injector.wiring import inject, Provide
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Horizontal, Container
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Footer, Label
from textual.widgets._toggle_button import ToggleButton
from watchdog.events import FileSystemEvent

from terry.domain.terraform.core.entities import (
    TerraformVersion,
)
from terry.domain.terraform.workspaces.entities import Workspace
from terry.infrastructure.file_system.exceptions import ReadFileException, DeleteDirException, DeleteFileException
from terry.infrastructure.file_system.services import FileSystemService
from terry.infrastructure.operation_system.services import OperationSystemService
from terry.infrastructure.shared.command_utils import clean_up_command_output
from terry.infrastructure.terraform.core.services import TerraformCoreService
from terry.infrastructure.terraform.workspace.exceptions import (
    TerraformWorkspaceListException,
    TerraformWorkspaceSwitchException,
)
from terry.infrastructure.terraform.workspace.services import WorkspaceService
from terry.presentation.cli.action_handlers.main import action_handler_registry
from terry.presentation.cli.messages.dir_activate_message import DirActivate
from terry.presentation.cli.messages.files_select_message import FileSelect
from terry.presentation.cli.messages.path_delete_message import PathDelete
from terry.presentation.cli.widgets.buttons.sidebar_button import SidebarButton
from terry.presentation.cli.widgets.resizable_rule import ResizingRule
from terry.presentation.cli.di_container import DiContainer
from terry.presentation.cli.entities.terraform_command_executor import TerraformCommandExecutor
from terry.presentation.cli.screens.add_file.main import AddFileScreen
from terry.presentation.cli.screens.main.constants import (
    MainScreenIdentifiers,
    Orientation,
    TERRAFORM_VERIFICATION_FAILED_MESSAGE,
    WORKSPACE_SWITCH_SUCCESS_TEMPLATE,
)
from terry.presentation.cli.screens.main.containers.commands_log import (
    CommandsLog,
)
from terry.presentation.cli.screens.main.containers.content import Content
from terry.presentation.cli.screens.main.containers.header import Header
from terry.presentation.cli.screens.main.containers.project_tree import ProjectTree
from terry.presentation.cli.screens.main.containers.state_files import StateFiles
from terry.presentation.cli.screens.main.containers.workspaces import Workspaces
from terry.presentation.cli.screens.main.helpers import get_or_raise_validate_terraform, validate_work_dir
from terry.presentation.cli.screens.main.mixins.resize_containers_watcher_mixin import ResizeContainersWatcherMixin
from terry.presentation.cli.screens.main.mixins.system_monitoring_mixin import SystemMonitoringMixin
from terry.presentation.cli.screens.main.mixins.terraform_action_handler_mixin import TerraformActionHandlerMixin
from terry.presentation.cli.screens.main.sidebars.history_sidebar import CommandHistorySidebar
from terry.presentation.cli.screens.search.main import SearchScreen
from terry.presentation.cli.themes.arctic import arctic_theme
from terry.presentation.cli.themes.github_dark import github_dark_theme
from terry.settings import (
    CommandStatus,
    TERRAFORM_MAIN_ACTIONS,
    TERRAFORM_ADDITIONAL_ACTIONS,
    SEVERITY_LEVEL_ERROR,
    SEVERITY_LEVEL_INFORMATION,
    DEFAULT_THEME,
    MAX_TABS_HOT_KEY,
)


class Terry(App, ResizeContainersWatcherMixin, TerraformActionHandlerMixin, SystemMonitoringMixin):
    """The main app for the Terry project."""

    __slots__ = [
        "work_dir",
        "active_dir",
        "workspace_service",
        "terraform_version",
        "file_system_service",
        "terraform_core_service",
        "operation_system_service",
    ]

    CSS_PATH = "styles.tcss"
    TITLE = "Terry"

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(key="ctrl+f", action="open_search", description="Search"),
        Binding(key="ctrl+shift+n", action="open_create_file", description="Create file"),
        *[
            Binding(key=f"ctrl+{index}", action=f"activate_tab({index})", show=False)
            for index in range(1, MAX_TABS_HOT_KEY + 1)
        ],
        *[
            Binding(action.shortcut, action=f'tf_request("{action.value}")', description=action.name)
            for action in TERRAFORM_MAIN_ACTIONS + TERRAFORM_ADDITIONAL_ACTIONS
        ],
        Binding("h", "toggle_history_sidebar", "History"),
        Binding("escape", "exit", "Exit sidebar", show=False),
    ]

    show_history_sidebar = reactive(False)

    @inject
    def __init__(
        self,
        *args,
        work_dir: Path | str = Provide[DiContainer.config.work_dir],
        workspace_service: WorkspaceService = Provide[DiContainer.workspace_service],
        file_system_service: FileSystemService = Provide[DiContainer.file_system_service],
        terraform_core_service: TerraformCoreService = Provide[DiContainer.terraform_core_service],
        operation_system_service: OperationSystemService = Provide[DiContainer.operation_system_service],
        **kwargs,
    ):
        """
        Initialize the Terry App with a specified working directory.

        Parameters:
            work_dir (Path or str): The directory path for the application's workspace.
            workspace_service (WorkspaceService): The service for managing Terraform workspaces.
            file_system_service (FileSystemService): The service for interacting with the file system.
            operation_system_service (OperationSystemService): The service for interacting with the operating system.
            terraform_core_service (TerraformCoreService): The service for interacting with Terraform core commands.
            *args: Variable length argument list to pass to the parent App constructor.
            **kwargs: Arbitrary keyword arguments to pass to the parent App constructor.
        Attributes:
            work_dir (Path): Normalized working directory path.
            workspace (str): Initial workspace name, set to "default".
        """
        super().__init__(*args, **kwargs)
        ResizeContainersWatcherMixin.__init__(self)
        TerraformActionHandlerMixin.__init__(self)
        SystemMonitoringMixin.__init__(self)

        self.work_dir: Path = work_dir if isinstance(work_dir, Path) else Path(work_dir)
        self.active_dir: Path = self.work_dir

        self.workspaces: List[Workspace] = []
        self.selected_workspace: Workspace | None = None
        self.terraform_version: TerraformVersion | None = None
        self._tf_command_executor: TerraformCommandExecutor | None = None

        self.workspace_service: WorkspaceService = workspace_service
        self.terraform_core_service: TerraformCoreService = terraform_core_service
        self.file_system_service: FileSystemService = file_system_service
        self.operation_system_service: OperationSystemService = operation_system_service

        # containers
        # Todo: create properties for these
        self.log_component: CommandsLog | None = None  # type: ignore
        self.workspaces_container: Workspaces | None = None
        self.project_tree_container: ProjectTree | None = None
        self.content: Content | None = None
        self.history_sidebar: CommandHistorySidebar | None = None

        self.active_resizing_rule: ResizingRule | None = None
        self.pause_system_monitoring = False

        self.validate_env()
        self.init_env()

        atexit.register(self.cleanup)

    def compose(self) -> ComposeResult:
        """
        Compose the user interface for the Terry application.

        This method sets up the application's layout and UI components, verifying the project type
        and rendering different views based on the project's status. It creates a structured
        terminal interface with multiple sections including workspaces, project tree, state files,
        search, content display, and command logs.

        Returns:
            ComposeResult: A generator yielding Textual UI components for rendering the application

        Raises:
            None explicitly, but may raise exceptions during component initialization

        Notes:
            - Hardcoded project verification (is_tf_project = True)
            - Supports multiple workspaces: default, development, staging, production
            - Dynamically lists state files from the working directory
            - Includes Header, Sidebar (Workspaces, ProjectTree, StateFiles),
              Content area (Search, Content), CommandsLog, and Footer
        """
        is_tf_project = True

        if not is_tf_project:
            yield from self.no_tf_container()
            return

        state_files = self.file_system_service.list_state_files()
        yield Header(TERRAFORM_MAIN_ACTIONS, TERRAFORM_ADDITIONAL_ACTIONS, id="header")
        with Horizontal(id=MainScreenIdentifiers.MAIN_CONTAINER_ID):
            with Vertical(id=MainScreenIdentifiers.SIDEBAR):
                with Workspaces(id=MainScreenIdentifiers.WORKSPACE_ID) as workspaces_container:
                    workspaces_container.selected_workspace = self.selected_workspace
                    workspaces_container.workspaces = self.workspaces
                    self.workspaces_container = workspaces_container

                yield ResizingRule(
                    id=MainScreenIdentifiers.RESIZE_RULE_WS_PT,
                    orientation=Orientation.HORIZONTAL.value,
                    classes="resize-handle",
                    prev_component_id=MainScreenIdentifiers.WORKSPACE_ID,
                    next_component_id=MainScreenIdentifiers.PROJECT_TREE_ID,
                )

                with ProjectTree(
                    id=MainScreenIdentifiers.PROJECT_TREE_ID, work_dir=self.work_dir
                ) as project_tree_container:
                    self.project_tree_container = project_tree_container

                yield ResizingRule(
                    id=MainScreenIdentifiers.RESIZE_RULE_PT_SF,
                    orientation=Orientation.HORIZONTAL.value,
                    classes="resize-handle",
                    prev_component_id=MainScreenIdentifiers.PROJECT_TREE_ID,
                    next_component_id=MainScreenIdentifiers.STATE_FILES_ID,
                )
                yield StateFiles(id=MainScreenIdentifiers.STATE_FILES_ID, state_files=state_files)

            yield ResizingRule(
                id=MainScreenIdentifiers.RESIZE_RULE_SR,
                orientation=Orientation.VERTICAL.value,
                classes="resize-handle",
                prev_component_id=MainScreenIdentifiers.SIDEBAR,
                next_component_id=MainScreenIdentifiers.RIGHT_PANEL,
            )
            with Vertical(id=MainScreenIdentifiers.RIGHT_PANEL):
                with Content(id=MainScreenIdentifiers.CONTENT_ID) as content:
                    self.content = content
                yield ResizingRule(
                    id=MainScreenIdentifiers.RESIZE_RULE_CC,
                    orientation=Orientation.HORIZONTAL.value,
                    classes="resize-handle",
                    prev_component_id=MainScreenIdentifiers.CONTENT_ID,
                    next_component_id=MainScreenIdentifiers.COMMANDS_LOG_ID,
                )
                with CommandsLog(id=MainScreenIdentifiers.COMMANDS_LOG_ID) as log_component:
                    self.log_component = log_component

            with Vertical(id=MainScreenIdentifiers.SIDE_MENU):
                yield SidebarButton(content="⥻", action=self.action_toggle_history_sidebar)
            with CommandHistorySidebar() as history_sidebar:
                self.history_sidebar = history_sidebar
        yield Footer()

    async def on_mount(self):
        """
        Handles the mounting process for the application. This method is asynchronously invoked
        when the application is mounted and performs necessary initialization tasks such as
        starting the system events monitoring and synchronization monitoring.
        """
        self.register_theme(arctic_theme)  # pyright: ignore [reportArgumentType]
        self.register_theme(github_dark_theme)  # pyright: ignore [reportArgumentType]

        self.theme = DEFAULT_THEME
        self.start_system_events_monitoring()
        self.start_sync_monitoring()

    def action_open_create_file(self) -> None:
        """
        Open the create file modal for the current working directory.

        This method pushes a CreateFileScreen onto the application's screen stack, initializing it with the current
        working directory. The create file modal allows users to create new files within the project.

        Returns:
            None
        """
        add_file_screen = AddFileScreen(
            self.file_system_service, self.work_dir, self.active_dir.relative_to(self.work_dir)
        )
        self.push_screen(add_file_screen)

    def write_command_log(self, message: str, status: CommandStatus, details: str = "") -> None:
        """
        Write a command log entry to the application's command log component.

        Parameters:
            message (str): The command or action being logged.
            status (CommandStatus): The execution status of the command ('SUCCESS' or 'ERROR').
            details(str): Additional details or context for the command log entry.

        Writes two log entries to the CommandsLog component:
            1. A basic command log with the message
            2. A detailed log entry with timestamp, message, and color-coded status

        The log entries use rich text formatting to highlight the message and status:
            - Successful commands are displayed in green with a checkmark (✅)
            - Error commands are displayed in red with a cross (❌)
            - Timestamps are displayed in a neutral gray color

        Side Effects:
            - Updates the CommandsLog widget with formatted log entries
        """
        if not self.log_component:
            return

        self.log_component.write_primary_message(message)
        self.log_component.write_datetime_status_message(message, status)
        if details:
            self.log_component.write_secondary_message(details)

    def update_selected_file_content(self, event: FileSystemEvent):
        """
        Updates the content of a selected file when a modification event occurs.

        Args:
            event (FileSystemEvent): The file system event containing information about the modified file.

        Note:
            This method only processes modification events for files that are currently open in the editor.
            It ignores directory events and non-modification events.
        """
        if not isinstance(event, FileSystemEvent):
            return
        if event.is_directory:
            return
        if event.event_type != "modified":
            return

        abs_changed_file_path = Path(event.src_path.decode() if isinstance(event.src_path, bytes) else event.src_path)
        if not abs_changed_file_path.exists():
            return

        changed_file_path = str(abs_changed_file_path.relative_to(self.work_dir))
        try:
            content_tabs = self.query_one(Content)
        except NoMatches:
            return
        if changed_file_path not in content_tabs.files_contents:
            return

        content = abs_changed_file_path.read_text()
        content_tabs.update(changed_file_path, content)

    def cleanup(self):
        """Stop and cleanup the file system observer."""
        self.cleanup_observer()
        if self._tf_command_executor:
            self._tf_command_executor.cancel()

    def watch_show_history_sidebar(self, show_history_sidebar: bool) -> None:
        """Set or unset visible class when reactive changes."""
        self.query_one(CommandHistorySidebar).toggle(show_history_sidebar)

    # ------------------------------------------------------------------------------------------------------------------
    # Environment methods
    # ------------------------------------------------------------------------------------------------------------------

    def validate_env(self):
        """
        Validate the environment before running the application.

        This method performs environment validation checks before running the application.
        It verifies that the working directory is valid and that the project is a Terraform project.

        Raises:
            ValueError: If the working directory is invalid or the project is not a Terraform project.
        """
        validate_work_dir(self.work_dir)
        self.terraform_version = get_or_raise_validate_terraform(self.terraform_core_service)

    def init_env(self):
        """
        Initializes the workspace environment. This method sets up the workspace
        by listing the directories within the provided working directory and sets
        the last synchronization date to the current date and time.
        """
        try:
            self.workspaces = self.workspace_service.list().workspaces
            self.selected_workspace = next((w for w in self.workspaces if w.is_active), None)
        except TerraformWorkspaceListException as e:
            self.notify(clean_up_command_output(str(e)), severity="error")
            self.log.error(str(e))

    def refresh_env(self):
        """
        Refreshes the workspace environments and updates the associated UI components.

        This method initiates the processing of refreshing the environment by notifying
        the user, fetching the list of available workspaces, and then updating the
        corresponding UI elements to reflect the latest environment state. Any relevant
        changes such as the last synchronization date or the workspace directory are
        reflected in the application.

        :raises RuntimeError: If the workspace directory does not exist or cannot be accessed.
        """

        self.refresh_workspaces()
        self.refresh_project_tree()

    def refresh_workspaces(self):
        """
        Refreshes the list of available workspaces and updates the corresponding UI components.

        This method fetches the list of available workspaces from the Terraform workspace service
        and updates the corresponding UI components to reflect the latest workspace state. It also
        updates the selected workspace in the workspaces container if the active workspace has changed.

        """
        try:
            self.workspaces = self.workspace_service.list().workspaces
        except TerraformWorkspaceListException as e:
            self.notify(str(e), severity="error")
            self.log.error(str(e))
            return

        if not self.workspaces_container:
            try:
                self.workspaces_container = self.query_one(Workspaces)
            except NoMatches:
                self.notify("Workspaces container not found.")
                return

        selected_workspace = next((w for w in self.workspaces if w.is_active), None)
        if selected_workspace and (
            not self.workspaces_container.selected_workspace
            or self.workspaces_container.selected_workspace.name != selected_workspace.name
        ):
            self.workspaces_container.workspaces = self.workspaces

    def refresh_project_tree(self):
        """
        Refreshes the project tree by reloading the work directory tree.

        This method reloads the work directory tree in the project tree container to reflect
        any changes made to the project directory structure. It ensures that the project tree
        is up-to-date with the latest changes in the working directory.

        """
        if not self.project_tree_container:
            try:
                self.project_tree_container = self.query_one(ProjectTree)
            except NoMatches:
                self.notify("Project tree container not found.")

        if not self.project_tree_container:
            return

        work_dir_tree = self.project_tree_container.work_dir_tree
        if work_dir_tree:
            work_dir_tree.reload()

    # ------------------------------------------------------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------------------------------------------------------
    async def on_dir_activate(self, message: DirActivate) -> None:
        """
        Handles the activation of a directory triggered by a specific event message.

        Updates the active directory used for file creation and other operations
        that require a current working context. The active directory must exist
        and be within the work directory.

        Args:
            message: The `DirActivate` message containing the path to activate.
        """
        self.active_dir = message.path

    async def on_file_select(self, message: FileSelect) -> None:
        """
        Handle the file double-clicked event in the Terry application.

        This method is triggered when a file is double-clicked in the project tree. It performs several key operations:
        - Validates and normalizes the file path relative to the working directory
        - Checks file path validity and existence
        - Reads the file content
        - Updates the Content widget with the file's text and path
        - Handles potential errors during file reading

        Args:
            message (FileSelect): Event containing the path of the double-clicked file

        Raises:
            ValueError: If the file path is not a Path object
            FileNotFoundError: If the specified file does not exist
            Exception: If there are issues reading the file content

        Side Effects:
            - Logs an info message about content refresh
            - Notifies user of file opening errors
            - Updates the Content widget with file contents and path
        """
        file_path = message.path
        if not str(file_path).startswith(str(self.work_dir)):
            file_path = self.work_dir / file_path

        try:
            content = self.file_system_service.read(file_path)
        except ReadFileException as e:
            self.notify(str(e), severity="error")
            return

        file_path = file_path.relative_to(self.work_dir)
        await self.query_one(Content).add(str(file_path), content, message.line)

    def on_path_delete(self, event: PathDelete):
        """
        Handles the event of a path deletion in the system.

        This method is triggered when a path associated with the system is deleted.
        The event contains information about the deleted path. The method processes
        the event and implements required on path deletion.
        """

        try:
            if event.is_dir:
                self.file_system_service.delete_dir(event.path)
            else:
                self.file_system_service.delete_file(event.path)

        except DeleteDirException as e:
            self.notify(str(e), severity="error")
            return
        except DeleteFileException as e:
            self.notify(str(e), severity="error")
            return

        self.refresh_project_tree()

    def on_workspaces_select_event(self, message: Workspaces.SelectEvent) -> None:
        """
        Handle the workspace change event in the Terry application.

        This method updates the current workspace, simulates a workspace selection status, and provides user
        notifications. It performs the following actions:
        - Updates the application's current workspace
        - Sends a notification to the user about the workspace change
        - Logs the workspace selection command with its status

        Parameters:
            message (Workspaces.SelectEvent): An event containing the new workspace name

        Side Effects:
            - Updates `self.workspace`
            - Triggers a user notification
            - Writes a command log entry

        Note:
            This is currently a simulated implementation with random status generation.
            Future improvements should include actual Terraform workspace selection logic.
        """
        workspace = message.workspace
        try:
            self.workspace_service.switch(workspace.name)
        except TerraformWorkspaceSwitchException as e:
            self.notify(str(e), severity="error")
            status = CommandStatus.ERROR
            self.notify(
                f"Failed to switch workspace to {workspace.name}.",
                severity=SEVERITY_LEVEL_ERROR,
            )
            if not self.selected_workspace:
                return
            try:
                workspaces_container: Workspaces = self.query_one(Workspaces)
                previous_workspace_toggle: ToggleButton = self.query_one(f"#{workspace.uuid}")  # type: ignore
                selected_workspace_toggle: ToggleButton = self.query_one(f"#{self.selected_workspace.uuid}")  # type: ignore
            except NoMatches:
                return

            workspaces_container.selected_workspace = self.selected_workspace
            previous_workspace_toggle.value = False
            selected_workspace_toggle.value = True

        else:
            status = CommandStatus.SUCCESS
            self.notify(WORKSPACE_SWITCH_SUCCESS_TEMPLATE.format(workspace.name), severity=SEVERITY_LEVEL_INFORMATION)
            self.selected_workspace = workspace

        log_message = f"terraform workspace select {workspace.name}"
        self.write_command_log(log_message, status, log_message)
        self.init_env()

    @staticmethod
    def no_tf_container():
        yield Container(
            Label(TERRAFORM_VERIFICATION_FAILED_MESSAGE),
            id=MainScreenIdentifiers.TERRAFORM_ERROR_MESSAGE_ID,
        )

    # ----------------------------------------------------------------------------------------------------------------
    # Hot keys handlers
    # ----------------------------------------------------------------------------------------------------------------

    def action_tf_request(self, action: str) -> None:
        """
        Handle the clickable label click event in the Terry application.

        This method processes the clickable label click events triggered by the user in the main screen.

        Args:
            action (str): The event containing the action to handle.

        Raises:
            Exception: If the action handler fails.
        """
        handler = action_handler_registry.get(action)
        if not handler:
            return
        handler(self).handle()

    def action_activate_tab(self, tab_number):
        if self.content is None:
            return
        self.content.activate(tab_number)

    def action_open_search(self) -> None:
        """
        Open the search modal for the current working directory.

        This method pushes a SearchScreen onto the application's screen stack, initializing it with the current working
        directory. The search modal allows users to search and interact with files within the project.

        Returns:
            None
        """
        self.push_screen(SearchScreen(self.work_dir))

    def action_exit(self):
        self.show_history_sidebar = False

    def action_toggle_history_sidebar(self) -> None:
        """Toggle the sidebar visibility."""
        self.show_history_sidebar = not self.show_history_sidebar
