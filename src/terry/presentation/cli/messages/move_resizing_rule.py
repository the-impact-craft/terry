from dataclasses import dataclass
from enum import Enum, auto

from textual.message import Message


# Todo: Move this enums module
class Orientation(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()


@dataclass
class MoveEvent:
    timestamp: float
    delta: int


@dataclass
class MoveResizingRule(Message):
    orientation: str
    delta: int
    previous_component_id: str
    next_component_id: str


@dataclass
class BaseResizingRule(Message):
    id: str


@dataclass
class SelectResizingRule(BaseResizingRule):
    pass


@dataclass
class ReleaseResizingRule(BaseResizingRule):
    pass
