import logging
import sys
from pathlib import Path


def setup_logging(
    log_file: Path,
    name: str = "mantekaseek",
    level: int = logging.INFO,
) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    has_file = any(
        isinstance(h, logging.FileHandler) and Path(h.baseFilename) == log_file.resolve()
        for h in logger.handlers
    )
    if not has_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    stream_handlers = [h for h in logger.handlers if type(h) is logging.StreamHandler]
    if not stream_handlers:
        stream_handler = logging.StreamHandler(sys.stderr)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    else:
        for sh in stream_handlers:
            if getattr(sh.stream, "closed", False):
                sh.stream = sys.stderr

    return logger
