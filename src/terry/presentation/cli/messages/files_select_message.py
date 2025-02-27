from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from textual.message import Message


@dataclass
class FileSelect(Message):
    path: Path
    line: Optional[int] = 0
