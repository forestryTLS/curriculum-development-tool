import logging
from pythonjsonlogger import jsonlogger
from pathlib import Path


logger = logging.getLogger(__name__)

current_file = Path(__file__).resolve()
base_dir = current_file.parents[2]
logs_dir = base_dir / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)

fileHandler = logging.FileHandler(logs_dir / "app.log")

jsonFmt = jsonlogger.JsonFormatter(
    "%(name)s %(asctime)s %(levelname)s %(filename)s %(lineno)s %(process)d %(message)s",
    rename_fields={"levelname": "severity", "asctime": "timestamp"},
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)

fileHandler.setFormatter(jsonFmt)

logger.addHandler(fileHandler)

logger.setLevel(logging.DEBUG)