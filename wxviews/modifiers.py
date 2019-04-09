'''Module with default modifiers'''

from typing import TypeVar, Callable, Tuple, Any
import wx
from wx import Event # pylint: disable=E0611
from wxviews.core import WxNode
from wxviews.node import WidgetNode

BindValue = TypeVar('BindValue', Callable[[Event], None], Tuple[Callable[[Event], None], dict])

def bind(node: WidgetNode, key: str, value: BindValue):
    '''Calls node bind method'''
    event = wx.__dict__[key]
    if not isinstance(value, tuple):
        value = (value, {})
    command, args = value
    node.bind(event, command, **args)

def sizer(node: WxNode, key: str, value: Any):
    '''Sets sizer argument'''
    if key == '':
        node.sizer_args = {**node.sizer_args, **value}
    else:
        node.sizer_args[key] = value
