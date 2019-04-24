from typing import TypeVar, Tuple, Callable

import wx
from wx import Event

from wxviews.widgets import WidgetNode

BindValue = TypeVar('BindValue', Callable[[Event], None], Tuple[Callable[[Event], None], dict])


def bind(node: WidgetNode, key: str, value: BindValue):
    """Calls node bind method"""
    event = wx.__dict__[key]
    if not isinstance(value, tuple):
        value = (value, {})
    command, args = value
    node.bind(event, command, **args)
