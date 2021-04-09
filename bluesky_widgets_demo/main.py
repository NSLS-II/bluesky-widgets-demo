import argparse

from bluesky_widgets.qt import gui_qt

from .app import DemoApp
from .settings import SETTINGS


def main(argv=None):
    print(__doc__)

    parser = argparse.ArgumentParser(description="bluesky-widgets demo")
    parser.add_argument("--zmq", help="0MQ address")
    parser.add_argument("--catalog", help="Databroker catalog")
    args = parser.parse_args(argv)

    with gui_qt("Demo App"):
        if args.catalog:
            import databroker

            SETTINGS.catalog = databroker.catalog[args.catalog]

        # Optional: Receive live streaming data.
        if args.zmq:
            SETTINGS.subscribe_to.append(args.zmq)
        app = DemoApp()  # noqa: 401


if __name__ == "__main__":
    main()
