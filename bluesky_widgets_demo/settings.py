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


class Settings:
    columns = columns
    catalog = None
    subscribe_to = []


SETTINGS = Settings()
