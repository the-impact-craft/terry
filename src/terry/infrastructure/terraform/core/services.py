import json
import subprocess
from pathlib import Path

from terry.domain.operation_system.services import BaseOperationSystemService
from terry.domain.terraform.core.entities import (
    TerraformVersion,
    ValidateSettings,
    TerraformValidateOutput,
)
from terry.domain.terraform.core.services import BaseTerraformCoreService
from terry.infrastructure.shared.command_utils import clean_up_command_output
from terry.infrastructure.terraform.core.commands_builders import TerraformValidateCommandBuilder
from terry.infrastructure.terraform.core.exceptions import (
    TerraformVersionException,
    TerraformValidateException,
)
from terry.settings import TERRAFORM_VERSION_TIMEOUT, TERRAFORM_VALIDATE_TIMEOUT


class TerraformCoreService(BaseTerraformCoreService):
    def __init__(self, work_dir: str | Path, operation_system_service: BaseOperationSystemService, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.work_dir = work_dir if isinstance(work_dir, str) else str(work_dir)
        self.operation_system_service = operation_system_service

    def version(self) -> TerraformVersion:
        """
        Get the version of Terraform installed on the system.

        This method executes the 'terraform version' command to retrieve the installed Terraform version.

        Returns:
            TerraformVersion: An object containing the Terraform version details.

        Raises:
            TerraformVersionException: If an error occurs while retrieving or parsing the Terraform version.
        """
        command = ["terraform", "version", "-json"]
        str_command = " ".join(command)
        try:
            process = subprocess.run(
                command,
                cwd=self.work_dir,
                capture_output=True,
                check=True,
                timeout=TERRAFORM_VERSION_TIMEOUT,  # 30 seconds should be sufficient for version check
            )
            output = process.stdout
            json_output = json.loads(output)
            return TerraformVersion(command=str_command, **json_output)
        except subprocess.TimeoutExpired as e:
            raise TerraformVersionException(str_command, f"Version check timed out after {e.timeout}s")
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.strip()
            raise TerraformVersionException(str_command, error_message)
        except json.JSONDecodeError as e:
            raise TerraformVersionException(str_command, f"Invalid version output format: {str(e)}")
        except Exception as e:
            raise TerraformVersionException(str_command, str(e))

    # TODO: remove pragma once the method is implemented
    def destroy(self):  # pragma: no cover
        """
        Destroy the Terraform-managed infrastructure.

        Executes the 'terraform destroy' command to remove all resources defined in the current Terraform
        configuration.

        Returns:
            tuple: A 3-tuple containing:
                - stdout (bytes): Standard output from the destroy command
                - stderr (bytes): Standard error output from the destroy command
                - returncode (int): Return code indicating the command's execution status (0 for success)

        Raises:
            subprocess.CalledProcessError: If the command fails to execute
        """
        process = subprocess.run(["terraform", "destroy"], capture_output=True)
        return process.stdout, process.stderr, process.returncode

    def validate(self, settings: ValidateSettings):
        """
        Validates Terraform configuration by invoking the `terraform validate` command
        using system subprocess, based on the provided settings. Cleans up the output
        in case of exceptions and wraps it in a custom exception for consistent handling.

        Args:
            settings: The validation settings specifying details for the `terraform validate`
                command execution.

        Raises:
            TerraformValidateException: Raised when validation fails due to timeout,
                command failure, or any unexpected error, encapsulating details of the
                command and additional diagnostic information.

        Returns:
            TerraformValidateOutput: The result of validation containing the executed
                command as a string and cleaned-up standard output.
        """
        command = TerraformValidateCommandBuilder().build_from_settings(settings)
        str_command = " ".join(command)
        try:
            process = subprocess.run(
                command,
                text=True,
                check=True,
                cwd=self.work_dir,
                capture_output=True,
                timeout=TERRAFORM_VALIDATE_TIMEOUT,
            )
            return TerraformValidateOutput(command=str_command, output=clean_up_command_output(process.stdout))
        except subprocess.TimeoutExpired as e:
            raise TerraformValidateException(str_command, f"Validation timed out after {e.timeout}s")
        except subprocess.CalledProcessError as e:
            raise TerraformValidateException(str_command, clean_up_command_output(e.stderr))
        except Exception as e:
            raise TerraformValidateException(str_command, clean_up_command_output(str(e)))
