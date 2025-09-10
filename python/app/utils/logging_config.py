import logging
from pythonjsonlogger import jsonlogger
import os


logger = logging.getLogger(__name__)

os.makedirs("./logs", exist_ok=True)

fileHandler = logging.FileHandler("./logs/app.log")

jsonFmt = jsonlogger.JsonFormatter(
    "%(name)s %(asctime)s %(levelname)s %(filename)s %(lineno)s %(process)d %(message)s",
    rename_fields={"levelname": "severity", "asctime": "timestamp"},
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)

fileHandler.setFormatter(jsonFmt)

logger.addHandler(fileHandler)

logger.setLevel(logging.DEBUG)