from dataclasses import dataclass
from typing import List

from textual.message import Message


@dataclass
class RerunCommandRequest(Message):
    command: List[str]
    run_in_modal: bool
    error_message: str
