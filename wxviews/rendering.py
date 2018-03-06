'''Customizing of wx parsing'''

from wx import App, Frame, Control
from pyviews.core.node import NodeArgs
from wxviews.widgets import AppNode, FrameNode, ControlNode

def convert_to_node(inst, args: NodeArgs):
    '''Wraps instance with ControlNode'''
    args = (inst, args['xml_node'], args['parent_context'])
    if isinstance(inst, App):
        return AppNode(*args)
    if isinstance(inst, Frame):
        return FrameNode(*args)
    return ControlNode(*args)
