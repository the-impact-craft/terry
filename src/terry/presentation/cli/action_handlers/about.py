import sys

from terry.presentation.cli.action_handlers.base import BaseTerraformActionHandler
from terry.presentation.cli.action_handlers.main import action_handler
from terry.presentation.cli.screens.about.main import AboutScreen


@action_handler("about")
class AboutHandler(BaseTerraformActionHandler):
    def handle(self, *args, **kwargs):
        terraform_version = (
            self.app.terraform_version.terraform_version if self.app.terraform_version else "(undefined)"
        )
        platform = self.app.terraform_version.platform if self.app.terraform_version else sys.platform

        self.app.push_screen(
            AboutScreen(
                terraform_version=terraform_version,
                platform=platform,
            )
        )
