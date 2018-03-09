'''Customizing of wx parsing'''

from wx import App, Frame, Control, Sizer, BoxSizer
from pyviews.core.node import NodeArgs
from wxviews.node import AppNode, FrameNode, ControlNode
from wxviews.sizers import SizerNode

def convert_to_node(inst, args: NodeArgs):
    '''Wraps instance with ControlNode'''
    node_args = (inst, args['xml_node'], args['parent_context'])
    if isinstance(inst, App):
        return AppNode(*node_args)
    if isinstance(inst, Frame):
        return FrameNode(*node_args)
    if isinstance(inst, Sizer):
        return SizerNode(*node_args, parent_node=args['parent_node'], parent=args['parent'])
    return ControlNode(*node_args)
