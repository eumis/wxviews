"""Module with default modifiers"""

from typing import TypeVar, Callable, Tuple, Any
from pyviews.core import Node
import wx
from wx import Event
from wxviews.core import Sizerable
from wxviews.node import WidgetNode, Style, StyleError

BindValue = TypeVar('BindValue', Callable[[Event], None], Tuple[Callable[[Event], None], dict])


def bind(node: WidgetNode, key: str, value: BindValue):
    """Calls node bind method"""
    event = wx.__dict__[key]
    if not isinstance(value, tuple):
        value = (value, {})
    command, args = value
    node.bind(event, command, **args)


def sizer(node: Sizerable, key: str, value: Any):
    """Sets sizer argument"""
    if key == '':
        node.sizer_args = {**node.sizer_args, **value}
    else:
        node.sizer_args[key] = value

#
# def style(node: Node, _: str, value: Any):
#     """Applies styles to node"""
#     keys = [key.strip() for key in style_keys.split(',')] \
#         if isinstance(style_keys, str) else style_keys
#     try:
#         for key in [key for key in keys if key]:
#             for item in node.node_styles[key]:
#                 item.apply(node)
#     except KeyError as key_error:
#         error = StyleError('Style is not found')
#         error.add_info('Style name', key_error.args[0])
#         raise error from key_error
