from textual.events import MouseDown, MouseUp
from textual.reactive import reactive
from textual.widgets import Rule

from terry.presentation.cli.messages.move_resizing_rule import (
    MoveEvent,
    MoveResizingRule,
    SelectResizingRule,
    ReleaseResizingRule,
)


class ResizingRule(Rule, can_focus=True):
    dragging: reactive[bool] = reactive(False)
    position: reactive[MoveEvent | None] = reactive(None)

    def __init__(self, prev_component_id, next_component_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not kwargs.get("id"):
            raise ValueError("ResizingRule must have an id")
        self.prev_component_id = prev_component_id
        self.next_component_id = next_component_id

    def on_mouse_down(self, event: MouseDown) -> None:
        """Start dragging when the separator is clicked."""
        self.dragging = True
        self.post_message(SelectResizingRule(id=self.id))  # type: ignore

    def on_mouse_up(self, event: MouseUp) -> None:
        """Stop dragging when mouse is released."""
        self.cleanup()

    def watch_position(self):
        if not self.dragging:
            return

        if self.position is None:
            return

        self.post_message(
            MoveResizingRule(
                delta=self.position.delta,
                previous_component_id=self.prev_component_id,
                next_component_id=self.next_component_id,
                orientation=self.orientation,
            )
        )

    def cleanup(self):
        self.dragging = False
        self.position = None

        self.post_message(ReleaseResizingRule(id=self.id))  # type: ignore
