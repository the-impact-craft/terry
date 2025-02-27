from dataclasses import dataclass

from terry.domain.terraform.core.entities import ApplySettings
from terry.presentation.cli.messages.base_tf_action_request import BaseTfActionRequest


@dataclass
class ApplyActionRequest(BaseTfActionRequest):
    """
    Represents a request to apply Terraform changes.

    This class encapsulates the data required for the application of Terraform changes.
    It is used for transmitting and processing apply-related instructions.
    The purpose of
    this class is to provide a structured format for handling apply settings in the application.
    """

    settings: ApplySettings
