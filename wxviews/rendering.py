'''Customizing of wx parsing'''

from wx import App, Frame, Control, Sizer, BoxSizer
from pyviews.core.node import RenderArgs
from pyviews.rendering.core import create_inst
from wxviews.node import AppNode, ControlNode, FrameNode
from wxviews.sizers import SizerNode

_TYPE_TO_NODE_MAP = {
    App: AppNode,
    Frame: FrameNode
}

def convert_to_node(inst, args: RenderArgs):
    '''Wraps instance with ControlNode'''
    args['wx_inst'] = inst
    if isinstance(inst, Sizer):
        return create_inst(SizerNode, args)
    try:
        node_class = _TYPE_TO_NODE_MAP[inst.__class__]
        return create_inst(node_class, args)
    except KeyError:
        return create_inst(ControlNode, args)
