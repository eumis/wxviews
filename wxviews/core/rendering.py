"""Common"""

from typing import Any

from pyviews.core import InheritedDict, XmlAttr, XmlNode, Node
from pyviews.expression import is_expression, parse_expression, execute
from pyviews.rendering.common import RenderingContext
from wx import Sizer


class WxRenderingContext(RenderingContext):
    """wxviews rendering context"""

    @property
    def parent(self) -> Any:
        """parent control"""
        return self.get('parent', None)

    @parent.setter
    def parent(self, value: Any):
        self['parent'] = value

    @property
    def sizer(self) -> Sizer:
        """Current sizer"""
        return self.get('sizer', None)

    @sizer.setter
    def sizer(self, value: Sizer):
        self['sizer'] = value

    @property
    def node_styles(self) -> InheritedDict:
        """Node styles"""
        return self.get('node_styles', None)

    @node_styles.setter
    def node_styles(self, value: InheritedDict):
        self['node_styles'] = value


def get_attr_args(xml_node, namespace: str, node_globals: InheritedDict = None) -> dict:
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


def get_init_value(attr: XmlAttr, node_globals: InheritedDict) -> Any:
    """Evaluates attribute value and returns it"""
    stripped_value = attr.value.strip() if attr.value else ''
    if is_expression(stripped_value):
        body = parse_expression(stripped_value)[1]
        parameters = node_globals.to_dictionary() if node_globals else {}
        return execute(body, parameters)
    return attr.value


def get_wx_child_context(xml_node: XmlNode, parent_node: Node,
                         context: WxRenderingContext) -> WxRenderingContext:
    """Return child node context"""
    return WxRenderingContext({
        'parent_node': parent_node,
        'parent': context.parent,
        'node_globals': InheritedDict(parent_node.node_globals),
        'sizer': context.sizer,
        'xml_node': xml_node
    })
