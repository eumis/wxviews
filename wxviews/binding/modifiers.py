from typing import Tuple, Callable

import wx
from wx import Event

from wxviews.widgets import WidgetNode


def bind(node: WidgetNode, key: str, value: (Callable[[Event], None], Tuple[Callable[[Event], None], dict])):
    """Calls node bind method"""
    event = wx.__dict__[key]
    if not isinstance(value, tuple):
        value = (value, {})
    command, args = value
    node.bind(event, command, **args)
