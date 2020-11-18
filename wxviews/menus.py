"""Rendering pipeline for menus"""

from pyviews.core import InstanceNode, InheritedDict, XmlNode
from pyviews.pipes import render_children
from pyviews.rendering import RenderingPipeline, get_type
from wx import Frame, MenuBar, Menu

from wxviews.core import WxRenderingContext, apply_attributes, \
    get_attr_args, get_init_value
from wxviews.widgets import WxNode


def create_menu_node(context: WxRenderingContext) -> WxNode:
    """Creates node from xml node using namespace as module and tag name as class name"""
    inst_type = get_type(context.xml_node)
    args = get_attr_args(context.xml_node, 'init', context.node_globals)
    inst = inst_type(**args)
    return WxNode(inst, context.xml_node, node_globals=context.node_globals)


def get_menu_bar_pipeline() -> RenderingPipeline:
    """Return render pipeline for MenuBar"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        render_menu_children,
        set_to_frame
    ], create_node=create_menu_node, name='menu bar pipeline')


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
        apply_attributes,
        render_menu_children,
        set_to_menu_bar
    ], create_node=create_menu_node, name='menu pipeline')


def set_to_menu_bar(node: WxNode, context: WxRenderingContext):
    """Adds menu to parent MenuBar"""
    if not isinstance(context.parent, MenuBar):
        msg = 'parent for Menu should be MenuBar, but it is {0}'.format(context.parent)
        raise TypeError(msg)
    # context.parent.Append(node.instance, node.properties['title'].get())
    try:
        title_attr = next(attr for attr in node.xml_node.attrs if attr.name == 'title')
        title = get_init_value(title_attr, context.node_globals)
    except StopIteration:
        title = str(node.instance)
    context.parent.Append(node.instance, title)


def get_menu_item_pipeline() -> RenderingPipeline:
    """Returns rendering pipeline for menu item"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        set_to_menu
    ], create_node=create_menu_node, name='menu item pipeline')


def set_to_menu(node: InstanceNode, context: WxRenderingContext):
    """Adds menu item to parent Menu"""
    if not isinstance(context.parent, Menu):
        msg = 'parent for MenuItem should be Menu, but it is {0}'.format(context.parent)
        raise TypeError(msg)
    context.parent.Append(node.instance)
