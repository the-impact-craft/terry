from contextlib import contextmanager
from datetime import datetime

from dependency_injector.wiring import Provide
from textual.screen import Screen

from terry.domain.terraform.core.entities import TerraformFormatScope, FormatSettings
from terry.infrastructure.shared.command_process_context_manager import CommandProcessContextManager
from terry.infrastructure.shared.command_utils import process_stdout_stderr
from terry.infrastructure.terraform.core.commands_builders import (
    TerraformPlanCommandBuilder,
    TerraformInitCommandBuilder,
    TerraformApplyCommandBuilder,
    TerraformFormatCommandBuilder,
)
from terry.infrastructure.terraform.core.exceptions import TerraformValidateException
from terry.presentation.cli.action_handlers.main import action_handler_registry
from terry.presentation.cli.cache import TerryCache
from terry.presentation.cli.di_container import DiContainer
from terry.presentation.cli.entities.command_cache import CommandCache
from terry.presentation.cli.entities.terraform_command_executor import TerraformCommandExecutor
from terry.presentation.cli.messages.tf_apply_action_request import ApplyActionRequest
from terry.presentation.cli.messages.tf_format_action_request import FormatActionRequest
from terry.presentation.cli.messages.tf_init_action_request import InitActionRequest
from terry.presentation.cli.messages.tf_plan_action_request import PlanActionRequest
from terry.presentation.cli.messages.tf_rerun_command import RerunCommandRequest
from terry.presentation.cli.messages.tf_validate_action_request import ValidateActionRequest
from terry.presentation.cli.screens.main.containers.content import Content
from terry.presentation.cli.screens.tf_command_output.main import TerraformCommandOutputScreen
from terry.presentation.cli.widgets.clickable_tf_action_label import ClickableTfActionLabel
from terry.settings import CommandStatus


class TerraformActionHandlerMixin:
    required_methods = [
        "query_one",
        "notify",
        "log",
        "write_command_log",
        "push_screen",
    ]

    required_attributes = [
        "work_dir",
        "terraform_core_service",
    ]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        for attribute in cls.required_attributes:
            if not hasattr(cls, attribute):
                raise AttributeError(f"Class {cls.__name__} must have attribute {attribute}")

        for method in cls.required_methods:
            if not hasattr(cls, method) or not callable(getattr(cls, method)):
                raise TypeError(f"Class {cls.__name__} must implement method {method}")

    def on_clickable_tf_action_label_click_event(self, event: ClickableTfActionLabel.ClickEvent) -> None:
        """
        Handle the clickable label click event in the Terry application.

        This method processes the clickable label click events triggered by the user in the main screen.

        Args:
            event (ClickableTfActionLabel.Click): The event containing the action to handle.

        Raises:
            Exception: If the action handler fails.
        """
        handler = action_handler_registry.get(event.action)
        if not handler:
            return
        handler(self).handle()

    def on_format_action_request(self, event: FormatActionRequest) -> None:
        """
        Handle the format apply request event in the Terry application.

        This method processes the format apply request event triggered by the user in the format settings screen.

        Args:
            event (FormatActionRequest): The event containing the format settings to apply.

        Raises:
            Exception: If the format settings cannot be applied.
        """
        format_scope = None
        if event.format.value == TerraformFormatScope.CURRENT_FILE.value:
            content_tabs = self.query_one(Content)  # type: ignore
            format_scope = content_tabs.active_tab
            if not format_scope:
                self.notify("No file selected.", severity="warning")  # type: ignore
                return
        settings = FormatSettings(path=format_scope)

        command = TerraformFormatCommandBuilder().build_from_settings(settings)
        if self._tf_command_executor:
            self._tf_command_executor.cancel()

        worker = self.run_worker(  # type: ignore
            self.run_tf_action(command, "Failed to format."),
            exit_on_error=True,
            thread=True,
            group="tf_command_worker",
        )
        self._tf_command_executor = TerraformCommandExecutor(command=command, worker=worker)  # type: ignore

    def on_validate_action_request(self, event: ValidateActionRequest) -> None:
        """
        Handles the `ValidateActionRequest` event to validate and apply Terraform
        formatting for the specified scope. The handler determines the scope of
        formatting (e.g., the currently active file), processes the formatting via the
        Terraform core service, and provides user notifications for both success and
        failure cases. Command logs are updated accordingly.

        Args:
            event: An instance of `ValidateActionRequest` containing the format request
                details, such as the scope of formatting to be applied.
        """
        try:
            output = self.terraform_core_service.validate(event.settings)  # type: ignore
        except TerraformValidateException as ex:
            self._log_error("Project validation failed.", ex.command, ex.message)
            return
        self._log_success("Project has been validated.", output.command, output.output)

    async def on_plan_action_request(self, event: PlanActionRequest):
        """
        Handles the application of a plan request. It retrieves the content component, dynamically creates a tab for
        the plan, and initiates the execution of the plan using the corresponding event and tab.

        Arguments:
            event (PlanApplyRequest): The event containing the plan settings to apply.
        """
        output_screen = TerraformCommandOutputScreen()
        self.push_screen(output_screen)  # type: ignore
        command = TerraformPlanCommandBuilder().build_from_settings(event.settings)
        if self._tf_command_executor:
            self._tf_command_executor.cancel()

        worker = self.run_worker(  # type: ignore
            self.run_tf_action(command, "Failed to apply plan settings.", output_screen=output_screen),
            exit_on_error=True,
            thread=True,
            group="tf_command_worker",
        )
        self._tf_command_executor = TerraformCommandExecutor(command=command, worker=worker)  # type: ignore

    async def on_init_action_request(self, event: InitActionRequest):
        """
        Handles the initialization of apply request for the settings screen.

        This asynchronous method executes a sequence of steps to handle the initialization
        apply request by interacting with the content view, adding a specific tab, and
        initiating the application plan. It performs necessary operations upon receipt of
        an initialization apply request event.

        Args:
            event (InitActionRequest): The initialization apply request
                event that triggers this handler.
        """
        output_screen = TerraformCommandOutputScreen()
        self.push_screen(output_screen)  # type: ignore

        command = TerraformInitCommandBuilder().build_from_settings(event.settings)

        if self._tf_command_executor:
            self._tf_command_executor.cancel()

        worker = self.run_worker(  # type: ignore
            self.run_tf_action(command, error_message="Failed to apply plan settings.", output_screen=output_screen),
            exit_on_error=True,
            thread=True,
            group="tf_command_worker",
        )

        self._tf_command_executor = TerraformCommandExecutor(command=command, worker=worker)

    async def on_apply_action_request(self, event: ApplyActionRequest):
        """
        Handles the ApplyActionRequest event by executing a Terraform apply command.

        This method is invoked to handle requests for applying Terraform plans defined
        in the settings provided by the event. It initializes the Terraform environment,
        executes the apply command, and ensures the proper handling of command execution
        through a dedicated thread and worker.

        Args:
            event: The ApplyActionRequest event containing settings required for
                applying the Terraform plan.

        """
        output_screen = TerraformCommandOutputScreen()
        self.push_screen(output_screen)  # type: ignore
        command = TerraformApplyCommandBuilder().build_from_settings(event.settings)

        if self._tf_command_executor:
            self._tf_command_executor.cancel()

        worker = self.run_worker(  # type: ignore
            self.run_tf_action(command, error_message="Failed to apply settings.", output_screen=output_screen),
            exit_on_error=True,
            thread=True,
            group="tf_command_worker",
        )
        self._tf_command_executor = TerraformCommandExecutor(command=command, worker=worker)

    async def on_rerun_command_request(self, event: RerunCommandRequest):
        output_screen = None
        if event.run_in_modal:
            output_screen = TerraformCommandOutputScreen()
            self.push_screen(output_screen)  # type: ignore
        if self._tf_command_executor:
            self._tf_command_executor.cancel()
        worker = self.run_worker(  # type: ignore
            self.run_tf_action(event.command, error_message=event.error_message, output_screen=output_screen),
            exit_on_error=True,
            thread=True,
            group="tf_command_worker",
        )
        self._tf_command_executor = TerraformCommandExecutor(command=event.command, worker=worker)

    def on_terraform_command_output_screen_close(self, _: TerraformCommandOutputScreen.Close):
        if self._tf_command_executor:
            self._tf_command_executor.cancel()

    async def run_tf_action(
        self,
        tf_command: list[str],
        error_message: str,
        cache: TerryCache = Provide[DiContainer.cache],
        output_screen: Screen | None = None,
    ):
        """
        Executes an asynchronous plan based on the specified tab name and updates the UI
        elements to reflect the ongoing process. The method logs the corresponding command
        and its output in real time, providing detailed feedback to the user. In case of an
        error, appropriate notifications are shown, and the error is logged.

        Arguments:
            tf_command (list[str]): The Terraform command to execute.
            error_message (str): The error message to display in case of an error.
            cache (TerryCache): The cache instance to store the executed commands
            output_screen (Screen): The screen to display the command output.
        """

        tf_command_str = " ".join(tf_command)

        manager = CommandProcessContextManager(tf_command, str(self.work_dir))  # type: ignore
        self._tf_command_executor.command_process = manager  # type: ignore

        cache.extend(
            "commands",
            CommandCache(
                tf_command, datetime.now(), run_in_modal=output_screen is not None, error_message=error_message
            ),
        )  # type: ignore

        if self.history_sidebar:  # type: ignore
            self.history_sidebar.refresh_content()  # type: ignore

        with self.paused_system_monitoring():
            with manager as (stdin, stdout, stderr):
                self._handle_logs(tf_command_str, output_screen, stdin, stdout, stderr)

        if manager.error:
            self._log_error(error_message, tf_command_str, str(manager.error))
            return

    def _log_success(self, message: str, command, details: str):
        """
        Log the success of a Terraform command.

        This method logs the success of a Terraform command by writing the output and command to the log.

        Args:
            message (str): Command main message.
            command (str): The Terraform command that was executed
            details (str): The output of the Terraform command that was executed
        """
        self.notify(message, severity="information")  # type: ignore
        self.log.info(details)  # type: ignore
        self.write_command_log(command, CommandStatus.SUCCESS, details)  # type: ignore

    def _log_error(self, message: str, command: str, error_message: str):
        """
        Log the error of a Terraform command.

        This method logs the error of a Terraform command by writing the error and command to the log.

        Args:
            message (str): Command main message.
            command (str): The Terraform command that was executed
            error_message (str): The error message of the Terraform command that was executed
        """
        self.log.error(error_message)  # type: ignore
        self.notify(message, severity="error")  # type: ignore
        self.write_command_log(command, CommandStatus.ERROR, error_message)  # type: ignore

    def _get_ui_area(self):
        """Sets up the UI output area based on the background execution flag."""
        return self.app.query_one(TerraformCommandOutputScreen)  # type: ignore

    def _handle_logs(self, command, output_screen, stdin, stdout, stderr):
        """Handles logging the process output and updating the UI."""
        output = []

        if output_screen:
            with output_screen.stdin_context(stdin):
                for line in process_stdout_stderr(stdout, stderr):
                    output_screen.write_log(line)
                    output.append(line)
        else:
            for line in process_stdout_stderr(stdout, stderr):
                output.append(line)

        self._log_success("Command executed.", command, "\n".join(output))

    @contextmanager
    def paused_system_monitoring(self):
        try:
            self.pause_system_monitoring = True
            yield
        finally:
            self.pause_system_monitoring = False
