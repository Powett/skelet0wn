"""This module contains all currently usable nodes (:py:class:`Limb`\s) in the `skelet0wn` framework."""

from sys import stdout

from loguru import logger

from .limb import Limb

# Explicit reexport
__all__ = ["Limb"]

logger.remove()
logger.add(
    stdout,
    format="<blue>[{extra[name]}]</blue> > {extra[depth_pad]}<level>{message}</level>",
    filter="skelet0wn.limbs",
)
