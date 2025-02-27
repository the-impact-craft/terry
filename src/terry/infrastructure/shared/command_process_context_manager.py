import io
import subprocess
from typing import List, Tuple, Union, IO


class CommandProcessContextManager:
    def __init__(
        self,
        command: List[str],
        cwd: str | None = None,
        env_vars: dict[str, str] | None = None,
    ):
        """
        Initializes the ProcessContextManager.

        :param command: Command to execute as a list of strings (e.g., ["ls", "-la"]).
        :param cwd: Optional working directory for the command.
        :param timeout: Timeout for the subprocess execution.
        """
        self.command = command
        self.cwd = cwd
        self.process: subprocess.Popen | None = None
        self.env_vars = env_vars
        self.error = None

    def __enter__(self) -> Tuple[Union[IO, None], Union[IO, None], Union[IO, None]]:
        """
        Creates and starts the process when entering the context.

        :return: Tuple containing stdin, stdout, and stderr streams.
        """
        try:
            self.process = subprocess.Popen(
                self.command,
                cwd=self.cwd,
                env=self.env_vars,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,  # Returns strings instead of bytes
            )

            return self.process.stdin, self.process.stdout, self.process.stderr
        except Exception as e:
            return io.StringIO(), io.StringIO(), io.StringIO(str(e))

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Ensures the process is terminated and all resources (stdin, stdout, stderr) are closed upon exit.
        """
        self.terminate_process()
        if exc_type:
            self.error = exc_value
        return True

    def terminate_process(self):
        """
        Terminates the process and ensures all streams are closed.
        """
        try:
            if not self.process:
                return
            if self.process.stdin:
                self.process.stdin.close()
            if self.process.stdout:
                self.process.stdout.close()
            if self.process.stderr:
                self.process.stderr.close()
            if self.process:
                self.process.terminate()  # Gracefully terminate the process
            self.process = None
        except subprocess.TimeoutExpired:
            self.process.kill()  # type: ignore # Force kill if it doesn't terminate in time
            self.process = None
        except Exception:
            self.process = None
