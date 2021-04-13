"""
Extending and supplementing the models from bluesky-widgets
"""
from bluesky_widgets.models.search import Search
from bluesky_widgets.utils.event import Event


class SearchWithButton(Search):
    """
    A Search model with a method to handle a click event.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events.add(view=Event)


class SearchAndView:
    def __init__(self, search, auto_plot_builder):
        self.search = search
        self.auto_plot_builder = auto_plot_builder
        self.search.events.view.connect(self._on_view)

    def _on_view(self, event):
        catalog = self.search.selection_as_catalog
        if catalog is None:
            return
        for uid, run in catalog.items():
            self.auto_plot_builder.add_run(run, pinned=True)
