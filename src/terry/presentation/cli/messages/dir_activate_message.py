from dataclasses import dataclass
from pathlib import Path

from textual.message import Message


@dataclass
class DirActivate(Message):
    path: Path
