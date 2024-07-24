import os
from sys import stdout
from typing import Optional

from loguru import logger


def get_previous_name(name: str) -> Optional[str]:
    dot_index = name.rfind(".")
    nb = int(name[dot_index + 1 :])
    if dot_index == -1 or nb == 0:
        return None
    return name[:dot_index] + f".{str(nb-1)}"


def get_package_relative_path(relative_path: str) -> str:
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)


def logger_setup() -> None:
    logger.add(
        stdout, format="<green>[     MAIN     ]</green> > {message}", filter="__main__"
    )
