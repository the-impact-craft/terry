from pathlib import Path

from terry.presentation.cli.di_container import DiContainer
from terry.presentation.cli.screens.main.main import Terry


def main(project_path: Path = Path.cwd()):  # pragma: no cover
    """
    Initialize and run the Terry command-line application.

    Launches the Terry App with a specified or default working directory. If no directory is provided,
    the current working directory is used as the default.

    Parameters:
        project_path (Path, optional): The directory path to initialize the application with.
                               Defaults to the current working directory if not specified.

    Example:
        # Run the app in the current directory
        main()

        # Run the app in a specific directory
        main(Path('/path/to/terraform/project'))
    """
    di_container = DiContainer()
    di_container.config.animation_enabled.from_value(True)
    di_container.config.work_dir.from_value(project_path)
    di_container.config.cache_dir.from_value(project_path / ".terry/.cache")
    di_container.wire(packages=["terry.presentation.cli"])
    app = Terry(work_dir=project_path)
    app.run()


if __name__ == "__main__":
    main(Path("/Users/bohdana_kuzmenko/PycharmProjects/tf"))
