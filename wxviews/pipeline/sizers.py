'''Rendering pipeline for SizerNode'''

# pylint: disable=W0613

from pyviews import RenderingPipeline
from pyviews.rendering.pipeline import render_children
from wxviews.core.sizers import SizerNode
from wxviews.pipeline.common import instance_node_setter, apply_attributes

def get_sizer_pipeline() -> RenderingPipeline:
    '''Returns rendering pipeline for SizerNode'''
    return RenderingPipeline(steps=[
        setup_setter,
        apply_attributes,
        render_sizer_children
    ])

def setup_setter(node: SizerNode, **args):
    '''Sets attr_setter for WxNode'''
    node.attr_setter = instance_node_setter

def render_sizer_children(node: SizerNode, **args):
    '''Renders sizer children'''
    render_children(node,
                    parent=node.instance,
                    node_globals=node.node_globals,
                    sizer=node.instance)
