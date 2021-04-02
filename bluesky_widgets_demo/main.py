from bluesky_widgets.models.search import Search
from bluesky_widgets.qt import gui_qt

from .app import DemoApp

def main(argv):
    print(__doc__)

    with gui_qt("Demo App"):
        app = DemoApp()

        # Optional: Receive live streaming data.
        if len(argv) > 1:
            from bluesky_widgets.qt.zmq_dispatcher import RemoteDispatcher
            from bluesky_widgets.utils.streaming import (
                stream_documents_into_runs,
            )

            address = argv[1]
            dispatcher = RemoteDispatcher(address)
            dispatcher.subscribe(stream_documents_into_runs(app.viewer.add_run))
            dispatcher.start()

        if len(argv) > 2:
            import databroker
            catalog = databroker.catalog[argv[2]]

            headings = (
                "Unique ID",
                "Scan ID",
                "Plan Name",
                "Scanning",
                "Start Time",
                "Duration",
                "Exit Status",
            )

            def extract_results_row_from_run(run):
                """
                Given a BlueskyRun, format a row for the table of search results.
                """
                from datetime import datetime

                metadata = run.describe()["metadata"]
                start = metadata["start"]
                stop = metadata["stop"]
                start_time = datetime.fromtimestamp(start["time"])
                motors = start.get("motors", "-")
                if stop is None:
                    str_duration = "-"
                else:
                    duration = datetime.fromtimestamp(stop["time"]) - start_time
                    str_duration = str(duration)
                    str_duration = str_duration[: str_duration.index(".")]
                return (
                    start["uid"][:8],
                    start.get("scan_id", "-"),
                    start.get("plan_name", "-"),
                    ", ".join(motors),
                    start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    str_duration,
                    "-" if stop is None else stop["exit_status"],
                )

            columns = (headings, extract_results_row_from_run)

            app.model.searches.append(Search(catalog, columns=columns))


if __name__ == "__main__":
    import sys

    main(sys.argv)