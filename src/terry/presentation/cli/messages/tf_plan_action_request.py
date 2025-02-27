from dataclasses import dataclass

from terry.domain.terraform.core.entities import PlanSettings
from terry.presentation.cli.messages.base_tf_action_request import BaseTfActionRequest


@dataclass
class PlanActionRequest(BaseTfActionRequest):
    """
    Represents a request to apply the plan settings.

    This class encapsulates data regarding the application of plan settings in a message.
    It is used for transmitting and processing plan-related instructions. The purpose of
    this class is to provide a structured format for handling plan settings in the application.

    """

    settings: PlanSettings
