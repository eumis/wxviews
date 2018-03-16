'''wxviews default modifiers'''

import wx
from pyviews.core.ioc import inject
from wxviews.node import ControlNode

def call(node, key, value):
    '''calls control method'''
    args = value if isinstance(value, list) or isinstance(value, tuple) else [value]
    method = getattr(node.wx_instance, key) if hasattr(node, 'wx_instance') else getattr(node, key)
    method(*args)

def setup_sizer(node: ControlNode, key, value):
    '''Modifier - sets argument for sizer add method'''
    if key == 'args':
        node.sizer_args = value
    if key == 'kwargs':
        node.sizer_kwargs = value

@inject('custom_events')
def bind(node: ControlNode, key, command, custom_events=None):
    '''Binds node to event'''
    source = custom_events if key in custom_events else wx.__dict__
    event = source[key]
    node.bind(event, command)
