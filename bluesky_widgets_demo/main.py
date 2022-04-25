import argparse

from bluesky_widgets.qt import gui_qt

import os

from .viewer import Viewer
from .settings import SETTINGS


def main(argv=None):
    print(__doc__)

    parser = argparse.ArgumentParser(description="bluesky-widgets demo")

    parser.add_argument(
        "--zmq-control-addr",
        default=None,
        help="Address of control socket of RE Manager. If the address "
        "is passed as a CLI parameter, it overrides the address specified with "
        "QSERVER_ZMQ_CONTROL_ADDRESS environment variable. Default address is "
        "used if the parameter or the environment variable are not specified.",
    )
    # parser.add_argument(
    #     "--zmq-info-addr",
    #     default=None,
    #     help="Address of PUB-SUB socket of RE Manager. If the address is passed as ""
    #     "a CLI parameter, it overrides the address specified with "
    #     "QSERVER_ZMQ_INFO_ADDRESS environment variable. Default address is "
    #     "used if the parameter or the environment variable are not specified.",
    # )

    parser.add_argument("--catalog", help="Databroker catalog")
    args = parser.parse_args(argv)

    zmq_control_addr = args.zmq_control_addr
    zmq_control_addr = zmq_control_addr or os.environ.get("QSERVER_ZMQ_CONTROL_ADDRESS", None)

    # zmq_info_addr = args.zmq_info_addr
    # zmq_info_addr = zmq_info_addr or os.environ.get("QSERVER_ZMQ_INFO_ADDRESS", None)

    with gui_qt("Demo App"):
        if args.catalog:
            import databroker

            SETTINGS.catalog = databroker.catalog[args.catalog]

        # Optional: Receive live streaming data.
        if args.zmq:
            SETTINGS.subscribe_to.append(zmq_control_addr)

        viewer = Viewer()  # noqa: 401


if __name__ == "__main__":
    main()
