"""Contains core nodes for wxviews"""

from abc import ABC, abstractmethod


class Sizerable(ABC):
    """Has arguments for sizer"""

    @property
    @abstractmethod
    def sizer_args(self) -> dict:
        pass

    @sizer_args.setter
    def sizer_args(self, value):
        pass
