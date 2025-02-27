from enum import Enum


# ------------------------------------------------------------------------------------------
# Ids
# ------------------------------------------------------------------------------------------


class MainScreenIdentifiers:
    """
    Contains the identifiers for the main screen components.
    """

    MAIN_CONTAINER_ID = "main_container"
    HEADER_ID = "header"
    FOOTER_ID = "footer"
    SIDEBAR = "sidebar"
    RIGHT_PANEL = "right_panel"
    SIDE_MENU = "side_menu"

    WORKSPACE_ID = "workspaces"
    PROJECT_TREE_ID = "project_tree"
    STATE_FILES_ID = "state_files"
    CONTENT_ID = "content"
    COMMANDS_LOG_ID = "commands_log"
    TERRAFORM_ERROR_MESSAGE_ID = "tf-error-message"

    RESIZE_RULE_WS_PT = "resize_rule_ws_pt"
    RESIZE_RULE_PT_SF = "resize_rule_pt_sf"
    RESIZE_RULE_SR = "resize_rule_sr"
    RESIZE_RULE_CC = "resize_rule_cc"


# ------------------------------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------------------------------
class Orientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


# ------------------------------------------------------------------------------------------
# Messages
# ------------------------------------------------------------------------------------------

TERRAFORM_VERIFICATION_FAILED_MESSAGE = "💥 Failed to verify terraform project 💥"
WORKSPACE_SWITCH_SUCCESS_TEMPLATE = "Workspace has been changed to {}."
