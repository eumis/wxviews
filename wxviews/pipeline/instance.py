'''Rendering pipeline for WxNode'''

# pylint: disable=W0613

from pyviews import RenderingPipeline
from pyviews.rendering.pipeline import apply_attribute, render_children
from wxviews.core.node import WxNode

def get_wx_pipeline() -> RenderingPipeline:
    '''Returns rendering pipeline for WxNode'''
    return RenderingPipeline(steps=[
        setup_setter,
        apply_attributes,
        render_wx_children
    ])

def setup_setter(node: WxNode, **args):
    '''Sets attr_setter for WxNode'''
    node.attr_setter = _wx_setter

def _wx_setter(node: WxNode, key, value):
    if key in node.properties:
        node.properties[key].set(value)
    elif hasattr(node, key):
        setattr(node, key, value)
    elif hasattr(node.instance, key):
        setattr(node.instance, key, value)

def apply_attributes(node: WxNode, **args):
    '''Applies attributes for node'''
    attrs = [attr for attr in node.xml_node.attrs if attr.namespace != 'init']
    for attr in attrs:
        apply_attribute(node, attr)

def render_wx_children(node: WxNode, **args):
    '''Renders WxNode children'''
    render_children(node,
                    parent=node.instance,
                    node_globals=node.node_globals)

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
                    node_globals=node.node_globals)
