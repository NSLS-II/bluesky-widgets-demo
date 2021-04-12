"""
Extendeding and supplementing the widgets import bluesky-widgets
"""
from bluesky_widgets.models.plot_builders import Lines
from bluesky_widgets.models.plot_specs import Figure, Axes
from bluesky_widgets.qt.search import QtSearch
from bluesky_widgets.qt.figures import QtFigures
from bluesky_widgets.qt.run_engine_client import (
    QtReEnvironmentControls,
    QtReManagerConnection,
    QtReQueueControls,
    QtReExecutionControls,
    QtReStatusMonitor,
    QtRePlanQueue,
    QtRePlanHistory,
)
from qtpy.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QComboBox,
    QLabel,
    QTabWidget,
)

from .models import SearchAndView


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
        # self.model.auto_plot_builder to access AutoLines
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

        self.x_selector.setEditable(True)
        self.y_selector.setEditable(True)

        self.x_selector.setCurrentIndex(-1)
        self.y_selector.setCurrentIndex(-1)

        new_button.clicked.connect(self._on_new_button_clicked)
        add_button.clicked.connect(self._on_add_button_clicked)
        active_search_model = self.model.search
        active_search_model.events.active_run.connect(self._on_active_run_selected)

    def _on_active_run_selected(self, event):
        # Could be None --> need to check
        print("_on_active_run_selected")
        self.x_selector.clear()
        self.y_selector.clear()
        # FIXME? How do I get all the stream_names?
        # Hardcoding to primary and baseline for now
        stream_names = ["primary", "baseline"]
        for stream in stream_names:
            self.x_selector.addItems(self.model.search.active_run[stream].to_dask().keys())
            self.y_selector.addItems(self.model.search.active_run[stream].to_dask().keys())

    def _on_new_button_clicked(self):
        print("New clicked")
        axes = Axes()
        figure = Figure((axes,), title="")
        print(self.x_selector.currentText())
        print(self.y_selector.currentText())
        line = Lines(x=self.x_selector.currentText(), ys=[self.y_selector.currentText()], axes=axes, max_runs=3)

        if self.model.search.active_run:
            line.add_run(self.model.search.active_run)

        self.model.auto_plot_builder.plot_builders.append(line)
        self.model.auto_plot_builder.figures.append(figure)

    def _on_add_button_clicked(self):
        print("Add clicked")
        # To handle new x value for current plot
        # --> New Lines instance

        # Loop through plot_builders and find active one
        # --> append to its ys


class QtSearchAndView(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QtSearchWithButton(model.search))
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(QtAddCustomPlot(self.model))
        plot_layout.addWidget(QtFigures(model.auto_plot_builder.figures))
        layout.addLayout(plot_layout)


class QtRunEngineManager(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(QtReManagerConnection(model))
        hbox.addWidget(QtReEnvironmentControls(model))
        hbox.addWidget(QtReQueueControls(model))
        hbox.addWidget(QtReExecutionControls(model))
        hbox.addWidget(QtReStatusMonitor(model))

        hbox.addStretch()
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        hbox.addWidget(QtRePlanQueue(model))
        hbox.addWidget(QtRePlanHistory(model))
        vbox.addLayout(hbox)
        # vbox.addStretch()
        self.setLayout(vbox)


class QtViewer(QTabWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        self.setTabPosition(QTabWidget.West)

        self._re_manager = QtRunEngineManager(model.run_engine)
        # TODO: putting the widget in QScrollArea doesn't work (the widget is not scaled with the window)
        #   It can be a configuration problem.
        self.addTab(self._re_manager, "Run Engine")

        self._search_and_view = QtSearchAndView(SearchAndView(model.search, model.auto_plot_builder))
        self.addTab(self._search_and_view, "Data Broker")
