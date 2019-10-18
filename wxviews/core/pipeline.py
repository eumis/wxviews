"""Common pipeline functionality"""

from pyviews.core.node import Node, InstanceNode
from pyviews.rendering.pipeline import apply_attribute

from wxviews.core import WxRenderingContext
from .node import Sizerable


def setup_instance_node_setter(node: InstanceNode, _: WxRenderingContext):
    """Sets attr_setter for WidgetNode"""
    node.attr_setter = instance_node_setter


def instance_node_setter(node: InstanceNode, key, value):
    """Sets default wxviews attr_setter"""
    if key in node.properties:
        node.properties[key].set(value)
    elif hasattr(node, key):
        setattr(node, key, value)
    elif hasattr(node.instance, key):
        setattr(node.instance, key, value)


def apply_attributes(node: Node, _: WxRenderingContext):
    """Applies attributes for node"""
    attrs = [attr for attr in node.xml_node.attrs if attr.namespace not in ['init']]
    for attr in attrs:
        apply_attribute(node, attr)


def add_to_sizer(node: (InstanceNode, Sizerable), context: WxRenderingContext):
    """Adds to wx instance to sizer"""
    if context.sizer is None:
        return
    context.sizer.Add(node.instance, **node.sizer_args)
