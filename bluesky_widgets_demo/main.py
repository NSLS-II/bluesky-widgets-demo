import argparse
import sys

from bluesky_widgets.models.search import Search
from bluesky_widgets.qt import gui_qt

from .app import DemoApp
from .qt_viewer_with_search import SearchWithButton

def main(argv=None):
    print(__doc__)

    parser = argparse.ArgumentParser(
        description="bluesky-widgets demo"
    )
    parser.add_argument('--zmq', help="0MQ address")
    parser.add_argument('--catalog', help="Databroker catalog")
    args = parser.parse_args(argv)

    with gui_qt("Demo App"):
        # Optional: Receive live streaming data.
        if args.zmq:
            from bluesky_widgets.qt.zmq_dispatcher import RemoteDispatcher
            from bluesky_widgets.utils.streaming import (
                stream_documents_into_runs,
            )

            address = args.zmq
            dispatcher = RemoteDispatcher(address)
            dispatcher.subscribe(stream_documents_into_runs(app.viewer.add_run))
            dispatcher.start()

        if args.catalog:
            import databroker
            catalog = databroker.catalog[args.catalog]

            headings = (
                "Scan ID",
                "Plan Name",
                "Scanning",
                "Start Time",
                "Duration",
                "Unique ID",
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
                    start.get("scan_id", "-"),
                    start.get("plan_name", "-"),
                    ", ".join(motors),
                    start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    str_duration,
                    start["uid"][:8],
                )

            columns = (headings, extract_results_row_from_run)

            app = DemoApp(SearchWithButton(catalog, columns=columns))


if __name__ == "__main__":
    main()
