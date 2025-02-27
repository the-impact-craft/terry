import json
import subprocess
from unittest.mock import patch, Mock

import pytest

from terry.domain.terraform.core.entities import (
    TerraformVersion,
)
from terry.infrastructure.terraform.core.exceptions import (
    TerraformVersionException,
)
from terry.infrastructure.terraform.core.services import TerraformCoreService


class TestTerraformCoreService:
    def test_init_with_string_path(self, temp_dir, operation_system_service):
        service = TerraformCoreService(str(temp_dir), operation_system_service)
        assert isinstance(service.work_dir, str)
        assert service.work_dir == str(temp_dir)

    def test_init_with_path_object(self, temp_dir, operation_system_service):
        service = TerraformCoreService(temp_dir, operation_system_service)
        assert isinstance(service.work_dir, str)
        assert service.work_dir == str(temp_dir)

    def test_version_success(self, terraform_service):
        terraform_version = "1.5.0"
        terraform_platform = "linux_amd64"
        terraform_outdated = False

        mock_version = {
            "terraform_version": terraform_version,
            "platform": terraform_platform,
            "provider_selections": {},
            "terraform_outdated": terraform_outdated,
        }
        mock_result = Mock(stdout=json.dumps(mock_version).encode(), stderr=b"", returncode=0)

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = terraform_service.version()

            assert isinstance(result, TerraformVersion)
            assert result.terraform_version == terraform_version
            assert result.platform == terraform_platform
            assert result.terraform_outdated == terraform_outdated

            mock_run.assert_called_once_with(
                ["terraform", "version", "-json"],
                cwd=terraform_service.work_dir,
                capture_output=True,
                check=True,
                timeout=30,
            )

    def test_version_timeout(self, terraform_service):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(["terraform"], 30)):
            with pytest.raises(TerraformVersionException) as exc_info:
                terraform_service.version()
            assert "Version check timed out after 30s" in str(exc_info.value)

    def test_version_command_error(self, terraform_service):
        error = subprocess.CalledProcessError(1, ["terraform"], stderr="terraform not found")
        with patch("subprocess.run", side_effect=error):
            with pytest.raises(TerraformVersionException) as exc_info:
                terraform_service.version()
            assert "terraform not found" in str(exc_info.value)

    def test_version_invalid_json(self, terraform_service):
        mock_result = Mock(stdout=b"invalid json", stderr=b"", returncode=0)
        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(TerraformVersionException) as exc_info:
                terraform_service.version()
            assert "Invalid version output format" in str(exc_info.value)

    def test_version_general_error(self, terraform_service):
        with patch("subprocess.run", side_effect=Exception("Unexpected error")):
            with pytest.raises(TerraformVersionException) as exc_info:
                terraform_service.version()
            assert "Unexpected error" in str(exc_info.value)
