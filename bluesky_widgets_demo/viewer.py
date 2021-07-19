import os

from bluesky_widgets.models.auto_plot_builders import AutoLines, AutoImages
from bluesky_widgets.models.run_engine_client import RunEngineClient
from bluesky_widgets.qt import Window

from .widgets import QtViewer
from .models import SearchWithButton
from .settings import SETTINGS


class ViewerModel:
    """
    This encapsulates on the models in the application.
    """

    def __init__(self):
        self.search = SearchWithButton(SETTINGS.catalog, columns=SETTINGS.columns)
        self.auto_plot_builders = [AutoLines(max_runs=3), AutoImages(max_runs=1)]

        self.run_engine = RunEngineClient(
            zmq_server_address=os.environ.get("QSERVER_ZMQ_ADDRESS", None),
            zmq_subscribe_address=os.environ.get("QSERVER_ZMQ_CONSOLE_ADDRESS", None),
        )


class Viewer(ViewerModel):
    """
    This extends the model by attaching a Qt Window as its view.

    This object is meant to be exposed to the user in an interactive console.
    """

    def __init__(self, *, show=True, title="Demo App"):
        # TODO Where does title thread through?
        super().__init__()
        if SETTINGS.subscribe_to:
            from bluesky_widgets.qt.zmq_dispatcher import RemoteDispatcher
            from bluesky_widgets.utils.streaming import (
                stream_documents_into_runs,
            )

            for address in SETTINGS.subscribe_to:
                dispatcher = RemoteDispatcher(address)
                for auto_plot_builder in self.auto_plot_builders:
                    dispatcher.subscribe(stream_documents_into_runs(auto_plot_builder.add_run))
                dispatcher.start()
        widget = QtViewer(self)
        self._window = Window(widget, show=show)

    @property
    def window(self):
        return self._window

    def show(self):
        """Resize, show, and raise the window."""
        self._window.show()

    def close(self):
        """Close the window."""
        self._window.close()
