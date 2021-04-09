from bluesky_widgets.models.auto_plot_builders import AutoLines
from bluesky_widgets.models.run_engine_client import RunEngineClient
from bluesky_widgets.qt import Window

from .qt_viewer_with_search import SearchWithButton, SearchAndView, QtSearchAndView


class DemoApp:
    """
    A user-facing model composed with a Qt widget and window.

    A key point here is that the model `searches` is public and can be
    manipuated from a console, but the view `_window` and all Qt-related
    components are private. The public `show()` and `close()` methods are the
    only view-specific actions that are exposed to the user. Thus, this could
    be implemented in another UI framework with no change to the user-facing
    programmatic interface.
    """

    def __init__(self, search, *, show=True, title="Demo App"):
        super().__init__()
        self.title = title
        self.search = search
        self.viewer = AutoLines(max_runs=3)
        self.model = SearchAndView(self.search, self.viewer)
        self.model2 = RunEngineClient()
        widget = QtDemoWindow(self.model, self.model2)
        self._window = Window(widget, show=show)

        from bluesky_widgets.models.search import Search
        from bluesky_widgets.examples.utils.generate_msgpack_data import get_catalog
        from bluesky_widgets.examples.utils.add_search_mixin import columns

        # Initialize with a two search tabs: one with some generated example data...
        self.searches.append(Search(get_catalog(), columns=columns))
        # ...and one listing any and all catalogs discovered on the system.
        from databroker import catalog

        self.model.searches.append(Search(catalog, columns=columns))

    def show(self):
        """Resize, show, and raise the window."""
        self._window.show()

    def close(self):
        """Close the window."""
        self._window.close()
