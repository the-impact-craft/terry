from textual.app import ComposeResult
from textual.containers import Container, HorizontalScroll

from terry.domain.terraform.core.entities import TerraformCommand
from terry.presentation.cli.widgets.clickable_tf_action_label import (
    ClickableTfActionLabel,
)


class Header(Container):
    """The header of the app."""

    DEFAULT_CSS = """

    Header {
        height: 4;
        padding: 1;
        margin: 0;
    }

        .action-button {
            padding: 0 1;
            height: 2;
            margin: 0 1;
            border-bottom: solid grey;
            color: grey;

            &:hover {
                color: white;
                border-bottom: solid $block-cursor-background;
            }
            
            &:focus {
                color: white;
                border-bottom: solid $block-cursor-background;
            }
        }
        """

    def __init__(
        self,
        main_commands: list[TerraformCommand],
        additional_commands: list[TerraformCommand],
        *args,
        **kwargs,
    ):
        """
        Initialize a Header widget with main and additional commands.

        Parameters:
             main_commands (list[TerraformCommand]): A list of primary commands to be displayed in the header.
             additional_commands (list[TerraformCommand]): A list of supplementary commands to be displayed in the header.
             *args: Variable length argument list passed to the parent class constructor.
             **kwargs: Arbitrary keyword arguments passed to the parent class constructor.
        """
        super().__init__(*args, **kwargs)
        self.main_commands = main_commands
        self.additional_commands = additional_commands

    @staticmethod
    def create_action_label(action) -> ClickableTfActionLabel:
        """
        Create a label for an action with a tooltip displaying its shortcut and value.

         Parameters:
             action (Action): An action object containing name, value, and shortcut attributes.

         Returns:
                ClickableTfActionLabel: A clickable label styled with the "action-button" CSS class and a tooltip showing
                the action's keyboard shortcut and corresponding Terraform command.
         The label is styled with the "action-button" CSS class and includes a tooltip that shows
         the action's keyboard shortcut and corresponding Terraform command.
        """
        return ClickableTfActionLabel(
            action.name, id=action.value, name=action.value, classes="action-button"
        ).with_tooltip(f"{action.shortcut} | {('terraform ' if action.is_terraform_command else '')}{action.value}")

    def compose(self) -> ComposeResult:
        """
        Compose the header's content by generating action labels for main and additional commands.

        Returns:
             ComposeResult: A generator yielding labels for actions or a default label.
        """
        with HorizontalScroll():
            for action in self.main_commands + self.additional_commands:
                yield self.create_action_label(action)
