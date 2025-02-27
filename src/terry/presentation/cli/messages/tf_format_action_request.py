from dataclasses import dataclass

from textual.message import Message

from terry.domain.terraform.core.entities import FormatScope


@dataclass
class FormatActionRequest(Message):
    """
    Represents a request to apply a specific format scope in a given message.

    This class encapsulates data regarding the application of formatting
    scopes to a message. It is used for transmitting and processing
    formatting-related instructions. The purpose of this class is to
    encapsulate the formatting scope for structured and consistent
    messaging.

    Arguments:
        format: FormatScope
    """

    format: FormatScope
