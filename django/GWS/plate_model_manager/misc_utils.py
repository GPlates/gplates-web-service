import warnings
import logging

pmm_logger = logging.getLogger("pmm")


def my_warningformat(message, category, filename, lineno, line=None):
    return f"{filename}:{lineno}: {category.__name__}: {message}\n"


warnings.formatwarning = my_warningformat


def print_warning(msg):
    # warnings.warn(msg)
    pmm_logger.warn(msg)


def print_error(msg):
    pmm_logger.error(msg)
