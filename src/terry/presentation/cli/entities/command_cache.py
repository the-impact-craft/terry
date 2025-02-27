from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class CommandCache:
    command: List[str]
    executed_at: datetime
    run_in_modal: bool
    error_message: str
