from dataclasses import dataclass
from pathlib import Path

from textual.message import Message


@dataclass
class PathDelete(Message):
    path: Path
    is_dir: bool
