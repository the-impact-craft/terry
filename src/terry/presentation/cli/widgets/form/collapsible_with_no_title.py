from textual.app import ComposeResult
from textual.widgets import Collapsible

COLLAPSIBLE_SYMBOL = "collapsed_symbol"
EXPANDED_SYMBOL = "expanded_symbol"


class CollapsibleWithNoTitle(Collapsible):
    """
    Represents a collapsible UI element that does not have a title.

    This class extends the functionality of a collapsible component by
    automatically handling missing symbols and initializing with an
    empty title. It also provides a mechanism for composing its
    internal structure.

    :ivar title: The title of the collapsible component, initialized as an empty string.
    :type title: str
    """

    def __init__(self, *args, **kwargs):
        self.cleanup_kwargs(kwargs)

        super().__init__(*args, **kwargs)
        self.title = ""

    def cleanup_kwargs(self, kwargs):
        """
        Cleans up a dictionary of keyword arguments by ensuring specific keys are present.

        This method checks for the presence of specific symbols in the provided dictionary
        of keyword arguments. If the required symbols are absent, the method adds them with
        default empty string values. This is particularly useful for preparing the `kwargs`
        to ensure that certain expected keys are defined before proceeding with further
        operations.
        Arguments:
            kwargs: A dictionary of keyword arguments to be cleaned up.
        """
        if COLLAPSIBLE_SYMBOL not in kwargs:
            kwargs[COLLAPSIBLE_SYMBOL] = ""
        if EXPANDED_SYMBOL not in kwargs:
            kwargs[EXPANDED_SYMBOL] = ""

    def compose(self) -> ComposeResult:
        """
        Composes and yields a result created from the provided contents.

        This method processes internal contents represented by `_contents_list` and
        generates a `ComposeResult` object by utilizing the `Contents` component. The
        resultant structure is yielded for further processing or rendering within a
        larger application flow.
        """
        yield self.Contents(*self._contents_list)
