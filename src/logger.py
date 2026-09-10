import logging
import sys
from functools import cache


@cache
def get_logger(level: int = logging.INFO) -> logging.Logger:
    # Root
    logger = logging.getLogger()
    logger.setLevel(level)
    # Stdout
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    logger.addHandler(console)

    return logger
