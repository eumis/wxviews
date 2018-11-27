'''Rendering pipeline for SizerNode'''

# pylint: disable=W0613

from wx import Sizer # pylint: disable=E0611
from pyviews import RenderingPipeline
from pyviews.core.observable import InheritedDict
from pyviews.rendering.pipeline import render_children
from wxviews.core.sizers import SizerNode
from wxviews.pipeline.common import instance_node_setter, apply_attributes, add_to_sizer

def get_sizer_pipeline() -> RenderingPipeline:
    '''Returns rendering pipeline for SizerNode'''
    return RenderingPipeline(steps=[
        setup_setter,
        apply_attributes,
        add_to_sizer,
        render_sizer_children,
        set_sizer_to_parent
    ])

def setup_setter(node: SizerNode, **args):
    '''Sets attr_setter for WxNode'''
    node.attr_setter = instance_node_setter

def render_sizer_children(node: SizerNode, parent=None, **args):
    '''Renders sizer children'''
    render_children(node,
                    parent_node=node,
                    parent=parent,
                    node_globals=InheritedDict(node.node_globals),
                    sizer=node.instance)

def set_sizer_to_parent(node, parent=None, sizer=None, **args):
    '''Pass sizer to parent SetSizer'''
    if parent is not None and sizer is None:
        parent.SetSizer(node.instance)