"""Module with default modifiers"""

from typing import TypeVar, Callable, Tuple, Any, List
from pyviews.core import Node
import wx
from wx import Event
from wxviews.core import Sizerable
from wxviews.node import WidgetNode, StyleError

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


def style(node: Node, _: str, keys: List[str]):
    """Applies styles to node"""
    if isinstance(keys, str):
        keys = [key.strip() for key in keys.split(',') if key]
    try:
        node_styles = node.node_globals['_node_styles']
        for key in keys:
            for item in node_styles[key]:
                item.apply(node)
    except KeyError as key_error:
        error = StyleError('Style is not found')
        error.add_info('Style name', key_error.args[0])
        raise error from key_error
