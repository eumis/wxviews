"""Rendering pipeline for menus"""

from pyviews.pipes import render_children
from wx import Frame, MenuBar, Menu
from pyviews.core import InstanceNode, InheritedDict, XmlNode
from pyviews.rendering import RenderingPipeline

from wxviews.core import WxRenderingContext, setup_instance_node_setter, apply_attributes


def get_menu_bar_pipeline() -> RenderingPipeline:
    """Return render pipeline for MenuBar"""
    return RenderingPipeline(pipes=[
        setup_instance_node_setter,
        apply_attributes,
        render_menu_children,
        set_to_frame
    ])


def render_menu_children(node: InstanceNode, context: WxRenderingContext):
    """Renders sizer children"""
    render_children(node, context, _get_menu_child_context)


def _get_menu_child_context(child_xml_node: XmlNode, node: InstanceNode,
                            _: WxRenderingContext) -> WxRenderingContext:
    return WxRenderingContext({
        'parent_node': node,
        'parent': node.instance,
        'node_globals': InheritedDict(node.node_globals),
        'xml_node': child_xml_node
    })


def set_to_frame(node: InstanceNode, context: WxRenderingContext):
    """Sets menu bar for parent Frame"""
    if not isinstance(context.parent, Frame):
        msg = 'parent for MenuBar should be Frame, but it is {0}'.format(context.parent)
        raise TypeError(msg)
    context.parent.SetMenuBar(node.instance)


def get_menu_pipeline() -> RenderingPipeline:
    """Return render pipeline for Menu"""
    return RenderingPipeline(pipes=[
        setup_instance_node_setter,
        apply_attributes,
        render_menu_children,
        set_to_menu_bar
    ])


def set_to_menu_bar(node: InstanceNode, context: WxRenderingContext):
    """Adds menu to parent MenuBar"""
    if not isinstance(context.parent, MenuBar):
        msg = 'parent for Menu should be MenuBar, but it is {0}'.format(context.parent)
        raise TypeError(msg)
    # context.parent.Append(node.instance, node.properties['title'].get())
    context.parent.Append(node.instance, node.instance)


def get_menu_item_pipeline() -> RenderingPipeline:
    """Returns rendering pipeline for menu item"""
    return RenderingPipeline(pipes=[
        setup_instance_node_setter,
        apply_attributes,
        set_to_menu
    ])


def set_to_menu(node: InstanceNode, context: WxRenderingContext):
    """Adds menu item to parent Menu"""
    if not isinstance(context.parent, Menu):
        msg = 'parent for MenuItem should be Menu, but it is {0}'.format(context.parent)
        raise TypeError(msg)
    context.parent.Append(node.instance)
