import abc

from terry.domain.terraform.core.entities import (
    TerraformVersion,
    ValidateSettings,
)


class BaseTerraformCoreService(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def version(self) -> TerraformVersion:
        """
        Get the version of Terraform installed on the system.

        This method is an abstract method that must be implemented by subclasses to provide the specific mechanism for
        retrieving the Terraform version.

        Raises:
            NotImplementedError: Indicates that the method must be implemented by a concrete subclass.

        Returns:
            TerraformVersion: An object containing the Terraform version details.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def destroy(self):
        """
        Executes the Terraform destroy command to remove all resources defined in the current Terraform configuration.

        This method is an abstract method that must be implemented by subclasses to provide the specific mechanism for
        destroying infrastructure resources.

        Raises:
            NotImplementedError: Indicates that the method must be overridden by a concrete implementation in subclasses

        Returns:
            tuple: A tuple containing (stdout, stderr, return_code) of the destroy operation when implemented.
        """
        raise NotImplementedError

    @abc.abstractmethod
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
        raise NotImplementedError
