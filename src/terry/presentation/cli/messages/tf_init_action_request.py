from dataclasses import dataclass

from terry.domain.terraform.core.entities import InitSettings
from terry.presentation.cli.messages.base_tf_action_request import BaseTfActionRequest


@dataclass
class InitActionRequest(BaseTfActionRequest):
    """
    Represents a request to apply the init settings.

    This class encapsulates data regarding the application of init settings in a message.
    It is used for transmitting and processing init-related instructions. The purpose of
    this class is to provide a structured format for handling init settings in the application.

    """

    settings: InitSettings
