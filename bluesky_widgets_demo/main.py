import argparse

from bluesky_widgets.qt import gui_qt

from .viewer import Viewer
from .settings import SETTINGS


def main(argv=None):
    print(__doc__)

    parser = argparse.ArgumentParser(description="bluesky-widgets demo")
    parser.add_argument("--document-stream", nargs="*", help="Address of streaming data source, e.g. zmq://...")
    parser.add_argument("--run-engine-worker", help="Address of RunEngine worker, e.g. zmq://...")
    parser.add_argument("--catalog", help="Databroker catalog")
    args = parser.parse_args(argv)

    with gui_qt("Demo App"):
        if args.catalog:
            import databroker

            SETTINGS.catalog = databroker.catalog[args.catalog]
        SETTINGS.subscribe_to.extend(args.document_stream or [])
        SETTINGS.run_engine_worker_address = args.run_engine_worker
        viewer = Viewer()  # noqa: 401


if __name__ == "__main__":
    main()
