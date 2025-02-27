from dataclasses import dataclass
from typing import Any

from textual.message import Message


@dataclass
class BaseTfActionRequest(Message):
    """Represents the base action request for Terraform operations.

    This class serves as a foundational structure for action requests in
    Terraform operations. It is designed to facilitate communication with
    underlying services or modules related to Terraform infrastructure
    requests. Subclasses may extend this class with more specific
    functionality and attributes as needed.
    """

    settings: Any
