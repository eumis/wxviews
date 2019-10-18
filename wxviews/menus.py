"""Rendering pipeline for menus"""

from wx import Frame, MenuBar, Menu
from pyviews.core import InstanceNode, Property, InheritedDict
from pyviews.rendering import RenderingPipeline, render_children

from wxviews.core import WxRenderingContext
from wxviews.core.pipeline import setup_instance_node_setter, apply_attributes


def get_menu_bar_pipeline() -> RenderingPipeline:
    """Return render pipeline for MenuBar"""
    return RenderingPipeline(steps=[
        setup_instance_node_setter,
        apply_attributes,
        render_menu_children,
        set_to_frame
    ])


def render_menu_children(node: InstanceNode, _: WxRenderingContext):
    """Renders sizer children"""
    render_children(node, WxRenderingContext({
        'parent_node': node,
        'parent': node.instance,
        'node_globals': InheritedDict(node.node_globals)
    }))


def set_to_frame(node: InstanceNode, context: WxRenderingContext):
    """Sets menu bar for parent Frame"""
    if not isinstance(context.parent, Frame):
        msg = 'parent for MenuBar should be Frame, but it is {0}'.format(context.parent)
        raise TypeError(msg)
    context.parent.SetMenuBar(node.instance)


def get_menu_pipeline() -> RenderingPipeline:
    """Return render pipeline for Menu"""
    return RenderingPipeline(steps=[
        add_menu_properties,
        setup_instance_node_setter,
        apply_attributes,
        render_menu_children,
        set_to_menu_bar
    ])


def add_menu_properties(node: InstanceNode, _: WxRenderingContext):
    """Adds menu specific properties to node"""
    node.properties['title'] = Property('title')


def set_to_menu_bar(node: InstanceNode, context: WxRenderingContext):
    """Adds menu to parent MenuBar"""
    if not isinstance(context.parent, MenuBar):
        msg = 'parent for Menu should be MenuBar, but it is {0}'.format(context.parent)
        raise TypeError(msg)
    context.parent.Append(node.instance, node.properties['title'].get())


def get_menu_item_pipeline() -> RenderingPipeline:
    """Returns rendering pipeline for menu item"""
    return RenderingPipeline(steps=[
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
