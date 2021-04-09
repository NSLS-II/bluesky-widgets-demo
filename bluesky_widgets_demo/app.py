from bluesky_widgets.models.auto_plot_builders import AutoLines
from bluesky_widgets.models.run_engine_client import RunEngineClient
from bluesky_widgets.qt import Window

from .qt_viewer_with_search import SearchWithButton, SearchAndView, QtSearchAndView
from .settings import SETTINGS


class ViewerModel:
    """
    This encapsulates on the models in the application.
    """
    def __init__(self):
        self.title = title
        self.search = search
        self.plot_builder = AutoLines(max_runs=3)
        self.model = SearchWithButton(SETTINGS.catalog, columns=SETTINGS.columns)
        self.run_engine = RunEngineClient()


class Viewer(ViewerModel):
    """
    This extends the model by attaching a Qt Window as its view.

    This object is meant to be exposed to the user in an interactive console.
    """

    def __init__(self, *, show=True, title="Demo App"):
        super().__init__()
        if SETTINGS.subscribe_to:
            from bluesky_widgets.qt.zmq_dispatcher import RemoteDispatcher
            from bluesky_widgets.utils.streaming import (
                stream_documents_into_runs,
            )

            for address in SETTINGS.subscribe_to:
                dispatcher = RemoteDispatcher(address)
                dispatcher.subscribe(stream_documents_into_runs(app.viewer.add_run))
                dispatcher.start()
        widget = QtDemoWindow(self.model, self.model2)
        self._window = Window(widget, show=show)

        self.model.searches.append(Search(catalog, columns=columns))
    
    @property
    def window(self):
        return self._window

    def show(self):
        """Resize, show, and raise the window."""
        self._window.show()

    def close(self):
        """Close the window."""
        self._window.close()
