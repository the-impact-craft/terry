from time import time
from typing import List, Tuple

from dependency_injector.wiring import Provide
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import ListView, ListItem, Label, Static

from terry.presentation.cli.cache import TerryCache
from terry.presentation.cli.di_container import DiContainer
from terry.presentation.cli.entities.command_cache import CommandCache
from terry.presentation.cli.messages.tf_rerun_command import RerunCommandRequest
from terry.presentation.cli.screens.main.sidebars.base import BaseSidebar
from terry.presentation.cli.utils import get_unique_id
from terry.settings import DOUBLE_CLICK_THRESHOLD


class CommandItem(Horizontal):
    DEFAULT_CSS = """
    CommandItem {
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
        
        
        & > .command {
            width: 90%;
            height: auto;
            & > Label { 
                width: 100%;
                color: $text-secondary
            }
            .timestamp {
                color:  $block-cursor-foreground;
            }
        }
        & > .repeat_button {
            width: 10%;
        }
    }
    """

    def __init__(self, command: List[str], timestamp, on_click_message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command = command
        self.timestamp = timestamp
        self.on_click_message = on_click_message

        self.last_command_click: Tuple[float, str] = (
            time() - 2,
            "",
        )

        if "id" not in kwargs:
            raise ValueError("CommandItem requires an id")

    def compose(self) -> ComposeResult:
        with Vertical(
            classes="command",
        ):
            yield Label(" ".join(self.command))
            yield Label(self.timestamp, classes="timestamp")

        yield Static("⤾", classes="repeat_button").with_tooltip("Repeat command")

    def on_click(self, _):
        current_click = (time(), self.id)

        if (
            current_click[0] - self.last_command_click[0] < DOUBLE_CLICK_THRESHOLD
            and current_click[1] == self.last_command_click[1]
        ):
            self.app.post_message(self.on_click_message)  # type: ignore

        self.last_command_click = current_click  # type: ignore


class CommandHistorySidebar(BaseSidebar):
    DEFAULT_CSS = """
    ListView {
        & > ListItem {
            &.-highlight {
                CommandItem {
                    & > .command {
                        & > Label { 
                             color:  $block-cursor-foreground;
                        }
                    }
                }
            }
        }
    }
    """

    commands: reactive[List[CommandCache]] = reactive([], recompose=True)

    def __init__(self, cache: TerryCache = Provide[DiContainer.cache], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = cache
        self.list_view = None

    def compose(self) -> ComposeResult:
        with ListView() as self.list_view:
            for command in reversed(self.commands):
                yield ListItem(
                    CommandItem(
                        id=get_unique_id(),
                        command=command.command,
                        timestamp=command.executed_at.isoformat(sep=" "),
                        on_click_message=RerunCommandRequest(
                            command=command.command,
                            run_in_modal=command.run_in_modal,
                            error_message=command.error_message,
                        ),
                    )
                )

    def toggle(self, visible: bool):
        self.set_class(visible, "-visible")
        if not self.list_view:
            return
        self.refresh_content()  # type: ignore
        self.list_view.focus()

    def on_mount(self, event):
        self.refresh_content()  # type: ignore

    @work(exclusive=True, thread=True)
    async def refresh_content(self):
        self.commands = self.cache.get("commands", [])  # type: ignore
