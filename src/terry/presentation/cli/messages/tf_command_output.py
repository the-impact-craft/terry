from dataclasses import dataclass

from textual.message import Message


@dataclass
class TfCommandOutput(Message):
    """
    Represents the output of a Terraform command.

    This class encapsulates the result of executing a Terraform command, providing an interface to manage and interact with the generated output string.

    Attributes:
        output (str): The string output generated from the Terraform command operation.
    """

    output: str
