from bluesky_widgets.models.auto_plot_builders import AutoLines
from bluesky_widgets.models.run_engine_client import RunEngineClient
from bluesky_widgets.qt import Window

from .widgets import QtViewer
from .models import SearchWithButton
from .settings import SETTINGS


class ViewerModel:
    """
    This encapsulates all the models in the application.
    """

    def __init__(self, title="Demo App"):
        # TODO We can remove SETTINGS here and make this cleaner once all of
        # the relevant parameters are runtime-settable, as in
        # self.search.catalog = ...
        # and
        # self.search.columns = ...
        # Once that is possible, the argparser and other entrypoints can instantiate
        # the app and then configure the instance without the potentially-confusing
        # SETTINGS side-band.
        self.title = title
        self.search = SearchWithButton(SETTINGS.catalog, columns=SETTINGS.columns)
        self.auto_plot_builder = AutoLines(max_runs=3)
        self.run_engine = RunEngineClient(SETTINGS.run_engine_worker_address)


class Viewer(ViewerModel):
    """
    This extends the model by attaching a Qt Window as its view.

    This object is meant to be exposed to the user in an interactive console.
    """

    def __init__(self, *, show=True, title="Demo App"):
        super().__init__(title=title)
        if SETTINGS.subscribe_to:
            from bluesky_widgets.qt.zmq_dispatcher import RemoteDispatcher
            from bluesky_widgets.utils.streaming import (
                stream_documents_into_runs,
            )

            for address in SETTINGS.subscribe_to:
                dispatcher = RemoteDispatcher(address)
                dispatcher.subscribe(stream_documents_into_runs(self.auto_plot_builder.add_run))
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
