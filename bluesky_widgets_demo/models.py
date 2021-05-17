"""
Extending and supplementing the models from bluesky-widgets
"""
from bluesky_widgets.models.search import Search
from bluesky_widgets.utils.event import Event

from functools import partial


class SearchWithButton(Search):
    """
    A Search model with a method to handle a click event.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events.add(view=Event)


class SearchAndView:
    def __init__(self, search, auto_plot_builders):
        self.search = search
        self.auto_plot_builders = auto_plot_builders
        self.search.events.view.connect(self._on_view)

        self._figures_to_lines = {}
        for auto_plot_builder in self.auto_plot_builders:
            auto_plot_builder.figures.events.added.connect(partial(self._on_figure_added, auto_plot_builder))

    def _on_view(self, event):
        catalog = self.search.selection_as_catalog
        if catalog is None:
            return
        for uid, run in catalog.items():
            for auto_plot_builder in self.auto_plot_builders:
                try:
                    auto_plot_builder.add_run(run, pinned=True)
                except TypeError:
                    auto_plot_builder.add_run(run)

    def _on_figure_added(self, auto_plot_builder, event):
        figure = event.item
        self._figures_to_lines[figure.uuid] = []
        for builder in auto_plot_builder.plot_builders:
            if builder.axes.figure.uuid == figure.uuid:
                self._figures_to_lines[figure.uuid].append(builder)
