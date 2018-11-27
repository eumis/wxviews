'''Rendering pipeline for WxNode'''

# pylint: disable=W0613

from pyviews import RenderingPipeline
from pyviews.core.observable import InheritedDict
from pyviews.rendering.pipeline import render_children
from wxviews.pipeline.common import instance_node_setter, apply_attributes, add_to_sizer
from wxviews.core.node import WxNode

def get_wx_pipeline() -> RenderingPipeline:
    '''Returns rendering pipeline for WxNode'''
    return RenderingPipeline(steps=[
        setup_setter,
        apply_attributes,
        add_to_sizer,
        render_wx_children
    ])

def setup_setter(node: WxNode, **args):
    '''Sets attr_setter for WxNode'''
    node.attr_setter = instance_node_setter

def render_wx_children(node: WxNode, sizer=None, **args):
    '''Renders WxNode children'''
    render_children(node,
                    parent=node.instance,
                    parent_node=node,
                    node_globals=InheritedDict(node.node_globals))

def get_frame_pipeline():
    '''Returns rendering pipeline for Frame'''
    return RenderingPipeline(steps=[
        setup_setter,
        apply_attributes,
        render_wx_children,
        lambda node, **args: node.instance.Show()
    ])

def get_app_pipeline():
    '''Returns rendering pipeline for App'''
    return RenderingPipeline(steps=[
        setup_setter,
        apply_attributes,
        render_app_children,
    ])

def render_app_children(node: WxNode, **args):
    '''Renders App children'''
    render_children(node,
                    node_globals=InheritedDict(node.node_globals))
