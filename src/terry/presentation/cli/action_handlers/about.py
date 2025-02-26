from terry.presentation.cli.action_handlers.base import BaseTerraformActionHandler
from terry.presentation.cli.action_handlers.main import action_handler
from terry.presentation.cli.screens.about.main import AboutScreen


@action_handler("about")
class AboutHandler(BaseTerraformActionHandler):
    def handle(self, *args, **kwargs):
        if not self.app.terraform_version:
            raise ValueError("Terraform version information is not available")
        self.app.push_screen(
            AboutScreen(
                terraform_version=self.app.terraform_version.terraform_version,
                platform=self.app.terraform_version.platform,
            )
        )
