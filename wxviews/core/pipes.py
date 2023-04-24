"""Common pipeline functionality"""

from pyviews.core.rendering import Node
from pyviews.pipes import apply_attribute

from wxviews.core.node import Sizerable
from wxviews.core.rendering import WxRenderingContext


def apply_attributes(node: Node, _: WxRenderingContext):
    """Applies attributes for node"""
    attrs = [attr for attr in node.xml_node.attrs if attr.namespace not in ['init']]
    for attr in attrs:
        apply_attribute(node, attr)


def add_to_sizer(node: Sizerable, context: WxRenderingContext):
    """Adds to wx instance to sizer"""
    if context.sizer is None:
        return
    context.sizer.Add(node.sizer_item, **node.sizer_args)
