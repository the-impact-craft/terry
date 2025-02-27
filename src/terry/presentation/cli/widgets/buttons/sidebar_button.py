from textual.widgets import Static


class SidebarButton(Static):
    DEFAULT_CSS = """
    SidebarButton {
        width: 5;
        border: round $secondary-background;
        padding: 0 1;
    }
    """

    def __init__(self, action, *args, **kwargs):
        self.action = action
        super().__init__(*args, **kwargs)

    def on_click(self):
        self.action()
