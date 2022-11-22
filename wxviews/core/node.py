"""Contains core nodes for wxviews"""

from abc import ABC, abstractmethod
from typing import Any


class Sizerable(ABC):
    """Has arguments for sizer"""

    def __init__(self):
        self._sizer_args: dict = {}

    @property
    def sizer_args(self) -> dict:
        """Sizer args"""
        return self._sizer_args

    @sizer_args.setter
    def sizer_args(self, value: dict):
        self._sizer_args = value

    @property
    @abstractmethod
    def sizer_item(self) -> Any:
        """instance to add to sizer"""
