"""Common"""

from typing import Any, Optional

from pyviews.core.expression import execute, is_expression, parse_expression
from pyviews.core.rendering import NodeGlobals
from pyviews.core.xml import XmlAttr, XmlNode
from pyviews.rendering.context import Node, RenderingContext
from wx import Sizer


class WxRenderingContext(RenderingContext):
    """wxviews rendering context"""

    @property
    def parent(self) -> Any:
        """parent control"""
        return self.get('parent')

    @parent.setter
    def parent(self, value: Any):
        self['parent'] = value

    @property
    def sizer(self) -> Sizer:
        """Current sizer"""
        return self.get('sizer')

    @sizer.setter
    def sizer(self, value: Sizer):
        self['sizer'] = value

    @property
    def node_styles(self) -> NodeGlobals:
        """Node styles"""
        return self.get('node_styles')

    @node_styles.setter
    def node_styles(self, value: NodeGlobals):
        self['node_styles'] = value


def get_attr_args(xml_node, namespace: str, node_globals: Optional[NodeGlobals] = None) -> dict:
    """Returns args from attributes with provided namespace"""
    init_attrs = [attr for attr in xml_node.attrs if attr.namespace == namespace]
    args = {}
    for attr in init_attrs:
        value = get_init_value(attr, node_globals)
        if attr.name == '':
            args = {**args, **value}
        else:
            args[attr.name] = value
    return args


def get_init_value(attr: XmlAttr, node_globals: Optional[NodeGlobals]) -> Any:
    """Evaluates attribute value and returns it"""
    stripped_value = attr.value.strip() if attr.value else ''
    if is_expression(stripped_value):
        body = parse_expression(stripped_value)[1]
        parameters = node_globals if node_globals else {}
        return execute(body, parameters)
    return attr.value


def get_wx_child_context(xml_node: XmlNode, parent_node: Node, context: WxRenderingContext) -> WxRenderingContext:
    """Return child node context"""
    return WxRenderingContext({
        'parent_node': parent_node,
        'parent': context.parent,
        'node_globals': NodeGlobals(parent_node.node_globals),
        'sizer': context.sizer,
        'xml_node': xml_node
    })
