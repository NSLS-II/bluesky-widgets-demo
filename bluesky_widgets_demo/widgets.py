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
    QtReRunningPlan,
    QtRePlanEditor,
    QtReConsoleMonitor,
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
        events = self.model.events
        if events is not None:
            events.view()


class QtAddCustomPlot(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        layout = QGridLayout()
        self.setLayout(layout)

        self.x_selector = QComboBox(self)
        self.y_selector = QComboBox(self)

        new_button = QPushButton("New")
        self.add_button = QPushButton("Add")
        self.add_button.setEnabled(False)

        layout.addWidget(QLabel("x axis:"), 0, 0, 1, 1)
        layout.addWidget(QLabel("y axis:"), 1, 0, 1, 1)
        layout.addWidget(self.x_selector, 0, 1, 1, 2)
        layout.addWidget(self.y_selector, 1, 1, 1, 2)
        layout.addWidget(new_button, 0, 3, 1, 1)
        layout.addWidget(self.add_button, 1, 3, 1, 1)

        self.x_selector.setEditable(True)
        self.y_selector.setEditable(True)

        self.x_selector.setCurrentIndex(-1)
        self.y_selector.setCurrentIndex(-1)

        new_button.clicked.connect(self._on_new_button_clicked)
        self.add_button.clicked.connect(self._on_add_button_clicked)
        active_search_model = self.model.search
        active_search_model.events.active_run.connect(self._on_active_run_selected)
        # Keep this on Lines only for now
        self.model.auto_plot_builders[0].figures.events.active_index.connect(self._on_active_figure_changed)
        self.x_selector.currentTextChanged.connect(self._on_x_selector_text_changed)

    def _on_active_run_selected(self, event):
        self.x_selector.clear()
        self.y_selector.clear()
        for stream in self.model.search.active_run:
            self.x_selector.addItems(self.model.search.active_run[stream].to_dask().keys())
            self.y_selector.addItems(self.model.search.active_run[stream].to_dask().keys())
        self.x_selector.addItem("time")
        self.y_selector.addItem("time")

    def _on_new_button_clicked(self):
        axes = Axes()
        figure = Figure((axes,), title="")
        line = Lines(x=self.x_selector.currentText(), ys=[self.y_selector.currentText()], axes=axes, max_runs=3)

        if self.model.search.active_run:
            line.add_run(self.model.search.active_run)

        # Keep this on Lines only for now
        self.model.auto_plot_builders[0].plot_builders.append(line)
        self.model.auto_plot_builders[0].figures.append(figure)

    def _on_add_button_clicked(self):
        # Keep this on Lines only for now
        if self.model.auto_plot_builders[0].figures.active_index is None:
            return
        active_index = self.model.auto_plot_builders[0].figures.active_index
        active_uuid = list(self.model._figures_to_lines.keys())[active_index]
        for line in self.model._figures_to_lines[active_uuid]:
            line.ys.append(self.y_selector.currentText())

    def _on_active_figure_changed(self, event):
        # Keep this on Lines only for now
        active_index = self.model.auto_plot_builders[0].figures.active_index
        active_figure = self.model.auto_plot_builders[0].figures[active_index]
        self.x_selector.setCurrentText(active_figure.axes[0].x_label)
        self.add_button.setEnabled(True)

    def _on_x_selector_text_changed(self, text):
        # Keep this on Lines only for now
        if self.model.auto_plot_builders[0].figures.active_index is None:
            return
        active_index = self.model.auto_plot_builders[0].figures.active_index
        active_figure = self.model.auto_plot_builders[0].figures[active_index]
        if text != active_figure.axes[0].x_label:
            self.add_button.setEnabled(False)
        else:
            self.add_button.setEnabled(True)


class QtSearchAndView(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QtSearchWithButton(model.search))
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(QtAddCustomPlot(self.model))
        # How would this work with a list of auto plot builders?
        for auto_plot_builder in self.model.auto_plot_builders:
            plot_layout.addWidget(QtFigures(auto_plot_builder.figures))
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
        vbox1 = QVBoxLayout()

        # Register plan editor (opening plans in the editor by double-clicking the plan in the table)
        pe = QtRePlanEditor(model)
        pq = QtRePlanQueue(model)
        pq.registered_item_editors.append(pe.edit_queue_item)

        vbox1.addWidget(pe, stretch=1)
        vbox1.addWidget(pq, stretch=1)
        hbox.addLayout(vbox1)
        vbox2 = QVBoxLayout()
        vbox2.addWidget(QtReRunningPlan(model), stretch=1)
        vbox2.addWidget(QtRePlanHistory(model), stretch=2)
        vbox2.addWidget(QtReConsoleMonitor(model), stretch=1)
        hbox.addLayout(vbox2)
        vbox.addLayout(hbox)
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

        self._search_and_view = QtSearchAndView(SearchAndView(model.search, model.auto_plot_builders))
        self.addTab(self._search_and_view, "Data Broker")
