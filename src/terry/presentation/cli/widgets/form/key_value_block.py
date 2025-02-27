from dataclasses import dataclass

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input
from textual.widgets import Static
from terry.presentation.cli.widgets.buttons.delete_button import DeleteButton
from terry.presentation.cli.widgets.buttons.view_secret_field_button import ViewSecretFieldButton


@dataclass
class KeyValueContent:
    key: str
    value: str


class KeyValueBlock(Horizontal):
    """
    Represents a horizontal UI block for inputting key-value pairs, with optional additional actions like delete or view.

    This class provides a UI block used to manage key-value pair inputs. It includes features for rendering two input
    fields for a key and a value, and additional optional buttons for delete and view actions. Users must provide
    a unique identifier (`id`) when initializing an instance of this class.

    Attributes:
        show_delete_button (bool): Indicates whether the delete button should be displayed.
        show_view_button (bool): Indicates whether the view button should be displayed.
    """

    DEFAULT_CSS = """
        KeyValueBlock {
            width: 100%;
            height: auto;
            padding_bottom: 1;
            padding_top: 0;

             & > Input {
                width: 45%;
                overflow-x: hidden;
             }

             & > Static {
                height: 3;
                padding: 1 1;
             }
        }
    """

    def __init__(
        self, key=None, value=None, show_delete_button=False, show_view_button=False, is_password=False, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.show_delete_button = show_delete_button
        self.show_view_button = show_view_button
        self.key = key
        self.value = value
        self.is_password = is_password

        if "id" not in kwargs:
            raise ValueError("id is required")

    @property
    def content(self):
        return KeyValueContent(key=self.children[0].value, value=self.children[1].value)  # type: ignore

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Key", value=self.key)
        yield Input(placeholder="Value", value=self.value, password=self.is_password)
        if self.show_delete_button:
            yield DeleteButton(content="x", component_id=self.id)
        if self.show_view_button:
            yield ViewSecretFieldButton(content="ᯆ", env_var_id=self.id)

    @on(DeleteButton.Click)
    def delete_key_value_block(self, event: DeleteButton.Click):
        if event.component_id == self.id:
            self.remove()

    @on(ViewSecretFieldButton.Click)
    def view_secret_field(self, _: ViewSecretFieldButton.Click):
        toggle: Static = self.children[2]  # type: ignore
        value_input: Input = self.children[1]  # type: ignore
        value_input.password = not value_input.password
        toggle.update("ᯆ" if value_input.password else "ᯣ")  # type: ignore
