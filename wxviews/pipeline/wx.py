'''Rendering pipeline for WidgetNode'''

# pylint: disable=W0613

from pyviews.core import InheritedDict
from pyviews.rendering import RenderingPipeline, render_children
from wxviews.node import WidgetNode
from .common import setup_instance_node_setter, apply_attributes, add_to_sizer

def get_wx_pipeline() -> RenderingPipeline:
    '''Returns rendering pipeline for WidgetNode'''
    return RenderingPipeline(steps=[
        setup_instance_node_setter,
        apply_attributes,
        add_to_sizer,
        render_wx_children
    ])

def render_wx_children(node: WidgetNode, **args):
    '''Renders WidgetNode children'''
    render_children(node,
                    parent=node.instance,
                    parent_node=node,
                    node_globals=InheritedDict(node.node_globals))

def get_frame_pipeline():
    '''Returns rendering pipeline for Frame'''
    return RenderingPipeline(steps=[
        setup_instance_node_setter,
        apply_attributes,
        render_wx_children,
        lambda node, **args: node.instance.Show()
    ])

def get_app_pipeline():
    '''Returns rendering pipeline for App'''
    return RenderingPipeline(steps=[
        setup_instance_node_setter,
        apply_attributes,
        render_app_children,
    ])

def render_app_children(node: WidgetNode, **args):
    '''Renders App children'''
    render_children(node,
                    parent_node=node,
                    node_globals=InheritedDict(node.node_globals))
