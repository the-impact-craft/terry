from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Container
from textual.css.query import NoMatches
from textual.widgets import Checkbox, Static

from terry.presentation.cli.widgets.clickable_icon import ClickableIcon
from terry.presentation.cli.widgets.form.collapsible_with_no_title import CollapsibleWithNoTitle


class CheckboxSettingBlock(Container):
    DEFAULT_CSS = """
    CheckboxSettingBlock {
        height: auto;

        & > Horizontal {
        height: auto;

        & > Checkbox {
          border: none;

          &:focus {
            border: none;
          }
        }
      }

      & > CollapsibleWithNoTitle {
        border-top: none;
        background: transparent;
        padding-bottom: 1;


        & > CollapsibleTitle {
          &:hover {
            background: transparent;
            color: $foreground;
          }

          &:focus {
            background: transparent;
          }
        }
      }
    }
    """

    def __init__(self, setting_name: str, label: str, description: str, **kwargs):
        self.setting_name = setting_name
        self.label = label
        self.description = description
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        with Horizontal(id=f"{self.setting_name}_block"):
            yield Checkbox(self.label, False, id=self.setting_name)
            yield ClickableIcon("(i)", name=self.setting_name)
        with CollapsibleWithNoTitle(collapsed=True, title="", id=f"{self.setting_name}_toggle"):
            yield Static(self.description)

    @on(ClickableIcon.Click)
    def handle_info_click(self, event: ClickableIcon.Click):
        """
        Handles the click event on the information icon.

        This method is called when the information icon is clicked by the user. It toggles
        the visibility of the associated information block, providing additional details
        about the selected setting.

        Arguments:
            event: An event representing the click action on the information icon.
        """
        try:
            collapsible: CollapsibleWithNoTitle = self.query_one(f"#{event.name}_toggle")  # type: ignore
        except NoMatches:
            return
        collapsible.collapsed = not collapsible.collapsed
