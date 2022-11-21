"""Bind setters"""

from typing import Any, Tuple, Callable, Union

import wx
from wx import Event, Sizer
from wx._core import wxAssertionError

from wxviews.widgets.rendering import WxNode


def bind(node: WxNode, key: str,
         value: Union[Callable[[Event], None], Tuple[Callable[[Event], None], dict]]):
    """Calls node bind method"""
    event = wx.__dict__[key]
    if not isinstance(value, tuple):
        value = (value, {})
    command, args = value
    node.bind(event, command, **args)

def show(node: WxNode, key: str, value: bool):
    """calls sizer.Show() if value is true and sizer.Hide() for false"""
    try:
        sizer: Sizer = node.node_globals[key]
        if value is None or value == sizer.IsShown(node.instance):
            return
        sizer.Show(node.instance, show=value)
        sizer.Layout()
    except wxAssertionError:
        sizer: Sizer = node.node_globals[key]
        wx.CallAfter(_show, sizer, node.instance, value)

def _show(sizer: Sizer, instance: Any, value: bool):
    sizer.Show(instance, show=value)
    sizer.Layout()
