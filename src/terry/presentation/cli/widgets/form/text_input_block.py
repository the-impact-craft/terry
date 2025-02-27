from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.css.query import NoMatches
from textual.widgets import Input, Static

from terry.presentation.cli.widgets.clickable_icon import ClickableIcon
from terry.presentation.cli.widgets.form.collapsible_with_no_title import CollapsibleWithNoTitle


class TextInputBlock(Container):
    DEFAULT_CSS = """
    TextInputBlock {
        height: auto;

        & > Horizontal {
            width: 100%;
            height: auto;
            padding_bottom: 1;
            padding_top: 0;

            & > Input {
                width: 65%
            }
            & > ClickableIcon {
                overflow-x: hidden;
                width: 35%;
                height: 3;
                padding: 1 1;
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
        self._input = None
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        self._input = Input()
        with Horizontal(id=f"{self.setting_name}_block"):
            yield ClickableIcon(f"{self.label} (i):", name=self.setting_name)
            yield self._input
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

    @property
    def content(self):
        if self._input is None:
            return None
        return self._input.value
