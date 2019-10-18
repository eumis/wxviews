"""Rendering pipeline for WidgetNode"""

from typing import Callable

from pyviews.core import InheritedDict, InstanceNode, XmlNode
from pyviews.rendering import RenderingPipeline, render_children
from wx import PyEventBinder, Event

from wxviews.core import Sizerable, WxRenderingContext
from wxviews.core.pipeline import setup_instance_node_setter, apply_attributes, add_to_sizer


class WidgetNode(InstanceNode, Sizerable):
    """Wrapper under wx widget"""

    Root: 'WidgetNode' = None

    def __init__(self, instance, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(instance, xml_node, node_globals=node_globals)
        self._sizer_args: dict = {}

    @property
    def sizer_args(self) -> dict:
        return self._sizer_args

    @sizer_args.setter
    def sizer_args(self, value):
        self._sizer_args = value

    def bind(self, event: PyEventBinder, handler: Callable[[Event], None], **args):
        """Binds handler to event"""
        self.instance.Bind(event, handler, **args)

    def destroy(self):
        super().destroy()
        self.instance.Destroy()


def get_wx_pipeline() -> RenderingPipeline:
    """Returns rendering pipeline for WidgetNode"""
    return RenderingPipeline(steps=[
        setup_instance_node_setter,
        apply_attributes,
        add_to_sizer,
        render_wx_children
    ])


def render_wx_children(node: WidgetNode, _: WxRenderingContext):
    """Renders WidgetNode children"""
    render_children(node, WxRenderingContext({
        'parent': node.instance,
        'parent_node': node,
        'node_globals': InheritedDict(node.node_globals)
    }))


def get_frame_pipeline():
    """Returns rendering pipeline for Frame"""
    return RenderingPipeline(steps=[
        setup_instance_node_setter,
        apply_attributes,
        render_wx_children,
        lambda node, ctx: node.instance.Show()
    ])


def get_app_pipeline():
    """Returns rendering pipeline for App"""
    return RenderingPipeline(steps=[
        store_root,
        setup_instance_node_setter,
        apply_attributes,
        render_app_children,
    ])


def store_root(node: WidgetNode, _: WxRenderingContext):
    """Store root node to global property"""
    WidgetNode.Root = node


def render_app_children(node: WidgetNode, _: WxRenderingContext):
    """Renders App children"""
    render_children(node, WxRenderingContext({
        'parent_node': node,
        'node_globals': InheritedDict(node.node_globals)
    }))


def get_root() -> WidgetNode:
    """returns root"""
    if WidgetNode.Root is None:
        raise ValueError("Root is not set")
    return WidgetNode.Root
