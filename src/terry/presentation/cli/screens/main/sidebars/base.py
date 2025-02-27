from textual.widget import Widget


class BaseSidebar(Widget):
    """
    Our sidebar widget.

    Add desired content to compose()

    """

    DEFAULT_CSS = """
    BaseSidebar {
        width: 40;
        /* Needs to go in its own layer to sit above content */
        layer: sidebar; 
        /* Dock the sidebar to the appropriate side */
        dock: right;
        /* Offset x to be -100% to move it out of view by default */
        offset-x: 100%;


        border-left: solid $secondary-background;
        border-top: solid $secondary-background;
        border-bottom: solid $secondary-background;
        border-title-color: $primary-lighten-2;

        /* Enable animation */
        transition: offset 200ms;

        &.-visible {
            /* Set offset.x to 0 to make it visible when class is applied */
            offset-x: 0;
        }

        & > Vertical {
            margin: 1 2;
        }
    }
    """
