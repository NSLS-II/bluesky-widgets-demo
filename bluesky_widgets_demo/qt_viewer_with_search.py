"""
Search for runs and visualize their data.

This example can be run alone as

$ python -m bluesky_widgets_demo.qt_viewer_with_search

# or with the data streaming utility which will print an address to connect to

# $ python -m bluesky_widgets.examples.utils.stream_data_zmq
# Connect a consumer to localhost:XXXXX

# python -m bluesky_widgets.examples.advanced.qt_viewer_with_search localhost:XXXXX
"""
from bluesky_widgets.models.search import SearchList, Search
from bluesky_widgets.qt.search import QtSearches
from bluesky_widgets.qt.figures import QtFigures
from bluesky_widgets.utils.event import Event
from bluesky_widgets.examples.utils.generate_msgpack_data import get_catalog
from bluesky_widgets.examples.utils.add_search_mixin import columns
from qtpy.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout

class SearchListWithButton(SearchList):
    """
    A SearchList model with a method to handle a click event.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events.add(view=Event)


class QtSearchListWithButton(QWidget):
    """
    A view for SearchListWithButton.

    Combines the QtSearches widget with a button that processes the selected Runs.
    """

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QtSearches(model))

        go_button = QPushButton("View Selected Runs")
        layout.addWidget(go_button)
        go_button.clicked.connect(self._on_go_button_clicked)

    def _on_go_button_clicked(self):
        self.model.events.view()


class SearchAndView:
    def __init__(self, searches, viewer):
        self.searches = searches
        self.viewer = viewer
        self.searches.events.view.connect(self._on_view)

    def _on_view(self, event):
        for uid, run in self.searches.active.selection_as_catalog.items():
            self.viewer.add_run(run, pinned=True)


class QtSearchAndView(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QtSearchListWithButton(model.searches))
        layout.addWidget(QtFigures(model.viewer.figures))
