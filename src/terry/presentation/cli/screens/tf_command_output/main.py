from contextlib import contextmanager
from dataclasses import dataclass
from typing import IO

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Input, TextArea


class CommandOutputComponent(Container):
    DEFAULT_CSS = """
        CommandOutputComponent {
            margin: 0 0;
            padding: 0 0;
        }
    """
    log_content = reactive("")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text_area = None

    # {'javascript', 'bash', 'markdown', 'html', 'java', 'python', 'json', 'yaml', 'regex', 'go', 'toml', 'rust', 'xml', 'css', 'sql'}
    def compose(self) -> ComposeResult:
        self.text_area = TextArea(
            text=self.log_content,
            language="toml",
            read_only=True,
            show_line_numbers=False,
        )
        yield self.text_area

    def watch_log_content(self):
        if self.log_content is not None and self.text_area is not None:
            self.text_area.load_text(self.log_content)
            self.text_area.scroll_end()


class TerraformCommandOutputScreen(ModalScreen):
    CONTAINER_ID = "terraform-command-output"
    BINDINGS = [("escape", "exit", "Pop screen")]
    CSS_PATH = "styles.tcss"
    stdin: reactive[IO[bytes] | None] = reactive(None)

    @dataclass
    class Close(Message):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log = None
        self._input_area: Input | None = None
        self.log_content_array = []

    def compose(self):
        self._log = CommandOutputComponent(id="log-content")
        self._input_area = Input(id="input-area")

        with Container(id=self.CONTAINER_ID):
            yield self._log
            yield self._input_area

    def write_log(self, log: str):
        self.log_content_array.append(log)
        command_output = self.query_one(CommandOutputComponent)

        if command_output is not None:
            command_output.log_content = "\n".join(self.log_content_array)

            if "Enter a value:" in log and self._input_area:
                self._input_area.focus()

    def watch_stdin(self):
        if self._input_area:
            self._input_area.disabled = self.stdin is None

    @on(Input.Submitted)
    def _on_input(self, message):
        if self.log_content_array:
            self.log_content_array[-1] += f" {message.value} \n"
        command_output = self.query_one(CommandOutputComponent)

        if command_output is not None:
            command_output.log_content = "\n".join(self.log_content_array)

        if self.stdin is None:
            self.log("STDIN is not available.")
            return

        self.stdin.write(f"{message.value}\n")  # type: ignore
        self.stdin.flush()
        if self._input_area:
            self._input_area.clear()
            self._input_area.blur()
        command_output.focus()

    def action_exit(self):
        self.post_message(self.Close())
        self.app.pop_screen()

    @contextmanager
    def stdin_context(self, stdin: IO[bytes]):
        self.stdin = stdin
        try:
            yield
        finally:
            self.stdin = None
            self.log("STDIN is closed.")
