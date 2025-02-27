from pathlib import Path
from typing import Union, Dict, List

from terry.domain.terraform.core.entities import (
    PlanSettings,
    InitSettings,
    ValidateSettings,
    ApplySettings,
    FormatSettings,
)


class TerraformPlanCommandBuilder:
    def __init__(self):
        self._command = ["terraform", "plan"]

    def set_refresh_only(self) -> "TerraformPlanCommandBuilder":
        self._command.append("-refresh-only")
        return self

    def set_destroy(self) -> "TerraformPlanCommandBuilder":
        self._command.append("-destroy")
        return self

    def set_no_refresh(self) -> "TerraformPlanCommandBuilder":
        self._command.append("-refresh=false")
        return self

    def add_inline_var(self, name: str, value: str) -> "TerraformPlanCommandBuilder":
        self._command.extend(["-var", f"{name}={value}"])
        return self

    def add_var_file(self, file: str) -> "TerraformPlanCommandBuilder":
        self._command.extend(["-var-file", file])
        return self

    def add_out(self, out: str) -> "TerraformPlanCommandBuilder":
        self._command.extend(["-out", out])
        return self

    def build(self) -> list[str]:
        return self._command

    def build_from_settings(self, settings: PlanSettings) -> list[str]:
        if settings.refresh_only:
            self.set_refresh_only()
        if settings.destroy:
            self.set_destroy()
        if settings.norefresh:
            self.set_no_refresh()
        if settings.inline_vars:
            for var in settings.inline_vars:
                if not var.name or not var.value:
                    continue
                self.add_inline_var(var.name, var.value)
        if settings.var_files:
            for var_file in settings.var_files:
                self.add_var_file(var_file)
        if settings.out:
            self.add_out(settings.out)
        return self.build()


class TerraformInitCommandBuilder:
    """Builder class for Terraform init commands."""

    def __init__(self):
        """Initialize the base terraform init command."""
        self.command = ["terraform", "init"]

    def add_disable_backend(self) -> "TerraformInitCommandBuilder":
        """Add the `-backend=false` flag."""
        self.command.append("-backend=false")
        return self

    def add_backend_config(self, backend_config: Dict[str, str]) -> "TerraformInitCommandBuilder":
        """Add backend configuration key-value pairs."""
        for key, value in backend_config.items():
            self.command.extend(["-backend-config", f"{key}={value}"])
        return self

    def add_backend_config_path(
        self, backend_config_path: Union[str, Path, List[str | Path]]
    ) -> "TerraformInitCommandBuilder":
        """Add backend configuration file(s)."""
        if isinstance(backend_config_path, list):
            for path in backend_config_path:
                self.command.extend(["-backend-config", f"{path}"])
        else:
            self.command.extend(["-backend-config", f"{backend_config_path}"])
        return self

    def add_force_copy(self) -> "TerraformInitCommandBuilder":
        """Add the `-force-copy` flag."""
        self.command.append("-force-copy")
        return self

    def add_disable_download(self) -> "TerraformInitCommandBuilder":
        """Add the `-get=false` flag."""
        self.command.append("-get=false")
        return self

    def add_disable_input(self) -> "TerraformInitCommandBuilder":
        """Add the `-input=false` flag."""
        self.command.append("-input=false")
        return self

    def add_disable_hold_lock(self) -> "TerraformInitCommandBuilder":
        """Add the `-lock=false` flag."""
        self.command.append("-lock=false")
        return self

    def add_plugin_dir(self, plugin_dir: Union[str, Path, List[str | Path]]) -> "TerraformInitCommandBuilder":
        """Add plugin directory or directories."""
        if isinstance(plugin_dir, list):
            for dir in plugin_dir:
                self.command.extend(["-plugin-dir", f"{dir}"])
        else:
            self.command.extend(["-plugin-dir", f"{plugin_dir}"])
        return self

    def add_reconfigure(self) -> "TerraformInitCommandBuilder":
        """Add the `-reconfigure` flag."""
        self.command.append("-reconfigure")
        return self

    def add_migrate_state(self) -> "TerraformInitCommandBuilder":
        """Add the `-migrate-state` flag."""
        self.command.append("-migrate-state")
        return self

    def add_upgrade(self) -> "TerraformInitCommandBuilder":
        """Add the `-upgrade` flag."""
        self.command.append("-upgrade")
        return self

    def add_ignore_remote_version(self) -> "TerraformInitCommandBuilder":
        """Add the `-ignore-remote-version` flag."""
        self.command.append("-ignore-remote-version")
        return self

    def add_test_directory(self, test_directory: Union[str, Path, list[str | Path]]) -> "TerraformInitCommandBuilder":
        """Add test directory or directories."""
        if isinstance(test_directory, list):
            for directory in test_directory:
                self.command.extend(["-test-directory", f"{directory}"])
        else:
            self.command.extend(["-test-directory", f"{test_directory}"])
        return self

    def build(self) -> list[str]:
        """Build and return the final terraform init command."""
        return self.command

    def build_from_settings(self, settings: InitSettings) -> list[str]:
        if settings.disable_backend:
            self.add_disable_backend()
        if settings.backend_config:
            self.add_backend_config(settings.backend_config)
        if settings.backend_config_path:
            self.add_backend_config_path(settings.backend_config_path)
        if settings.force_copy:
            self.add_force_copy()
        if settings.disable_download:
            self.add_disable_download()
        if settings.disable_input:
            self.add_disable_input()
        if settings.disable_hold_lock:
            self.add_disable_hold_lock()
        if settings.plugin_dir:
            if isinstance(settings.plugin_dir, list):
                for dir in settings.plugin_dir:
                    self.add_plugin_dir(dir)
            else:
                self.add_plugin_dir(settings.plugin_dir)
        if settings.reconfigure:
            self.add_reconfigure()
        if settings.migrate_state:
            self.add_migrate_state()
        if settings.upgrade:
            self.add_upgrade()
        if settings.ignore_remote_version:
            self.add_ignore_remote_version()
        if settings.test_directory:
            if isinstance(settings.test_directory, list):
                for directory in settings.test_directory:
                    self.add_test_directory(directory)
            else:
                self.add_test_directory(settings.test_directory)
        return self.build()


class TerraformValidateCommandBuilder:
    """Builder class for Terraform validate commands."""

    def __init__(self):
        """Initialize the base terraform validate command."""
        self.command = ["terraform", "validate"]

    def add_no_tests(self) -> "TerraformValidateCommandBuilder":
        """Add the `-no-tests` flag."""
        self.command.append("-no-tests")
        return self

    def add_test_directory(
        self, test_directory: Union[str, Path, list[str | Path]]
    ) -> "TerraformValidateCommandBuilder":
        """Add test directory or directories."""
        if isinstance(test_directory, list):
            for directory in test_directory:
                self.command.extend(["-test-directory", f"{directory}"])
        else:
            self.command.extend(["-test-directory", f"{test_directory}"])
        return self

    def build(self) -> list[str]:
        """Build and return the final terraform validate command."""
        return self.command

    def build_from_settings(self, settings: ValidateSettings) -> list[str]:
        if settings.no_tests:
            self.add_no_tests()
        if settings.test_directory:
            if isinstance(settings.test_directory, list):
                for directory in settings.test_directory:
                    self.add_test_directory(directory)
            else:
                self.add_test_directory(settings.test_directory)
        return self.build()


class TerraformApplyCommandBuilder:
    """Builder class for Terraform apply commands."""

    def __init__(self):
        """Initialize the base terraform apply command."""
        self.command = ["terraform", "apply"]

    def add_auto_approve(self) -> "TerraformApplyCommandBuilder":
        """Add the `-auto-approve` flag."""
        self.command.append("-auto-approve")
        return self

    def add_backup(self, backup: str | Path) -> "TerraformApplyCommandBuilder":
        """Add a backup file path."""
        self.command.extend(["-backup", str(backup)])
        return self

    def add_disable_backup(self) -> "TerraformApplyCommandBuilder":
        """Add the `-backup=-` flag."""
        self.command.append("-backup=-")
        return self

    def add_destroy(self) -> "TerraformApplyCommandBuilder":
        """Add the `-destroy` flag."""
        self.command.append("-destroy")
        return self

    def add_disable_lock(self) -> "TerraformApplyCommandBuilder":
        """Add the `-lock=false` flag."""
        self.command.append("-lock=false")
        return self

    def add_input(self) -> "TerraformApplyCommandBuilder":
        """Add the `-input` flag."""
        self.command.append("-input")
        return self

    def add_state(self, state: str | Path) -> "TerraformApplyCommandBuilder":
        """Add a state file path."""
        self.command.extend(["-state", str(state)])
        return self

    def add_state_out(self, state_out: str | Path) -> "TerraformApplyCommandBuilder":
        """Add a state output file path."""
        self.command.extend(["-state-out", str(state_out)])
        return self

    def app_plan_file(self, plan_file: str | Path) -> "TerraformApplyCommandBuilder":
        """Add a plan file path."""
        self.command.extend([str(plan_file)])
        return self

    def build(self) -> list[str]:
        """Build and return the final terraform apply command."""
        return self.command

    def build_from_settings(self, settings: ApplySettings) -> list[str]:
        if settings.auto_approve:
            self.add_auto_approve()
        if settings.backup:
            self.add_backup(settings.backup)
        if settings.disable_backup:
            self.add_disable_backup()
        if settings.destroy:
            self.add_destroy()
        if settings.disable_lock:
            self.add_disable_lock()
        if settings.input:
            self.add_input()
        if settings.state:
            self.add_state(settings.state)
        if settings.state_out:
            self.add_state_out(settings.state_out)
        if settings.plan:
            self.app_plan_file(f"{settings.plan[0]}")
        return self.build()


class TerraformFormatCommandBuilder:
    def __init__(self):
        """Initialize the base terraform apply command."""
        self.command = ["terraform", "fmt"]

    def add_path(self, path: str | Path) -> "TerraformFormatCommandBuilder":
        self.command.extend([str(path)])
        return self

    def build(self) -> list[str]:
        """Build and return the final terraform apply command."""
        return self.command

    def build_from_settings(self, settings: FormatSettings) -> list[str]:
        if settings.path:
            self.add_path(settings.path)
        return self.build()
