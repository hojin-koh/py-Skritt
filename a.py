
from Skritt.logging import ResourceFD6
from loguru import logger
import sys

logger.remove(0)
logger.add(sys.stderr, level="INFO", format="<level>{time:YYYYMMDD HHmmss} [{level.name[0]}]</level> {file}:{line} <level>{message}</level>")
logger.add('a.log', level="DEBUG", format="{time:YYYYMMDD HHmmss} [{level.name[0]}] {file}:{line} {message}")

logger.trace("Executing program")
logger.debug("Processing data...")
logger.info("Server started successfully.")
logger.success("Data processing completed successfully.")
logger.warning("Invalid configuration detected.")
logger.error("Failed to connect to the database.")
logger.critical("Unexpected system error occurred. Shutting down.")

def patcher(rec):
    rec['file'].name = 'pid'
    rec['line'] = 1689

logger2 = logger.patch(patcher)
logger2.info("AAAA")

import os
ResourceFD6(15)
print(os.fstat(15))
with os.fdopen(15, 'w') as fpw:
    fpw.write("666777\n")
    pass
for i in range(60):
    try:
        print(i, os.fstat(i))
    except:
        pass

import time
time.sleep(1000)
