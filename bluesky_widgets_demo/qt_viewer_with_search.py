"""
Search for runs and visualize their data.

This example can be run alone as

$ python -m bluesky_widgets_demo.qt_viewer_with_search

or with the data streaming utility which will print an address to connect to

$ python -m bluesky_widgets.examples.utils.stream_data_zmq
Connect a consumer to localhost:XXXXX

python -m bluesky_widgets.examples.advanced.qt_viewer_with_search localhost:XXXXX
"""
from bluesky_widgets.models.search import Search
from bluesky_widgets.models.plot_builders import Lines
from bluesky_widgets.models.plot_specs import Figure, Axes
from bluesky_widgets.qt.search import QtSearch
from bluesky_widgets.qt.figures import QtFigures
from bluesky_widgets.utils.event import Event
from bluesky_widgets.examples.utils.generate_msgpack_data import get_catalog
from bluesky_widgets.examples.utils.add_search_mixin import columns
from qtpy.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout,
                            QGridLayout, QComboBox, QLabel, QTabWidget)

class SearchWithButton(Search):
    """
    A Search model with a method to handle a click event.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events.add(view=Event)


class QtSearchWithButton(QWidget):
    """
    A view for SearchWithButton.

    Combines the QtSearch widget with a button that processes the selected Runs.
    """

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QtSearch(model))

        go_button = QPushButton("View Selected Runs")
        layout.addWidget(go_button)
        go_button.clicked.connect(self._on_go_button_clicked)

    def _on_go_button_clicked(self):
        self.model.events.view()


class QtAddCustomPlot(QWidget):
    def __init__(self, model, *args, **kwargs):
        # Can access self.model.searches to get active
        # self.model.viewer to access AutoLines
        super().__init__(*args, **kwargs)
        self.model = model
        print(type(self.model))
        layout = QGridLayout()
        self.setLayout(layout)

        self.x_selector = QComboBox(self)
        self.y_selector = QComboBox(self)

        new_button = QPushButton("New")
        add_button = QPushButton("Add")

        layout.addWidget(QLabel("x axis:"), 0, 0, 1, 1)
        layout.addWidget(QLabel("y axis:"), 1, 0, 1, 1)
        layout.addWidget(self.x_selector, 0, 1, 1, 2)
        layout.addWidget(self.y_selector, 1, 1, 1, 2)
        layout.addWidget(new_button, 0, 3, 1, 1)
        layout.addWidget(add_button, 1, 3, 1, 1)

        # x_selector notes:
        #   * Default to current x axis --> would mean have to find current active tab/plot_builder here?
        #   * If user changes to something else, disable add button
        # self.x_selector.addItems(['dcm_energy', 'def'])
        # self.y_selector.addItems(['I0', 'jkl'])

        self.x_selector.setEditable(True)
        self.y_selector.setEditable(True)

        self.x_selector.setCurrentIndex(-1)
        self.y_selector.setCurrentIndex(-1)

        new_button.clicked.connect(self._on_new_button_clicked)
        add_button.clicked.connect(self._on_add_button_clicked)
        active_search_model = self.model.search
        active_search_model.events.active_run.connect(self._on_active_run_selected)

    def _on_active_run_selected(self, event):
        # This is where x/y selectors would be populated
        # Could be None --> need to check
        print("_on_active_run_selected")
        self.x_selector.addItem('a')

    def _on_new_button_clicked(self):
        print("New clicked")
        axes = Axes()
        figure = Figure((axes,), title="")
        print(self.x_selector.currentText())
        print(self.y_selector.currentText())
        line = Lines(x=self.x_selector.currentText(),
                     ys=[self.y_selector.currentText()], max_runs=3)

        self.model.viewer.plot_builders.append(line)
        self.model.viewer.figures.append(figure)

    def _on_add_button_clicked(self):
        print("Add clicked")
        # To handle new x value for current plot
        # --> New Lines instance

        # Loop through plot_builders and find active one
        # --> append to its ys


class SearchAndView:
    def __init__(self, search, viewer):
        self.search = search
        self.viewer = viewer
        self.search.events.view.connect(self._on_view)

    def _on_view(self, event):
        for uid, run in self.search.active.selection_as_catalog.items():
            self.viewer.add_run(run, pinned=True)


class QtSearchAndView(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QtSearchWithButton(model.search))
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(QtAddCustomPlot(self.model))
        plot_layout.addWidget(QtFigures(model.viewer.figures))
        layout.addLayout(plot_layout)
