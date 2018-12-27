'''Module with default modifiers'''

from typing import TypeVar, Callable, Tuple
import wx
from wx import Event # pylint: disable=E0611
from wxviews.core.node import WxNode

BindValue = TypeVar('BindValue', Callable[[Event], None], Tuple[Callable[[Event], None], dict])

def bind(node: WxNode, key: str, value: BindValue):
    '''Calls node bind method'''
    event = wx.__dict__[key]
    if not isinstance(value, tuple):
        value = (value, {})
    command, args = value
    node.bind(event, command, **args)
