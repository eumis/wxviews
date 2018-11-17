'''Customizing of wx parsing'''

from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.observable import InheritedDict
from pyviews.core.compilation import Expression
from pyviews.core.node import Node
from pyviews.rendering.expression import is_code_expression, parse_expression
from pyviews.rendering.node import create_inst, get_inst_type
from wxviews.core.node import WxNode

def create_node(xml_node: XmlNode, node_globals: InheritedDict = None, **init_args) -> Node:
    '''Creates node from xml node using namespace as module and tag name as class name'''
    inst_type = get_inst_type(xml_node)
    args = {**init_args, **_get_init_args(xml_node, node_globals), **{'xml_node': xml_node}}
    inst = create_inst(inst_type, **args)
    if not isinstance(inst, Node):
        inst = WxNode(inst, xml_node, node_globals=node_globals)
    return inst

def _get_init_args(xml_node, node_globals: InheritedDict) -> dict:
    init_attrs = [attr for attr in xml_node.children if attr.namespace == 'init']
    return {attr.name: _get_init_value(attr, node_globals) for attr in init_attrs}

def _get_init_value(attr: XmlAttr, node_globals: InheritedDict):
    stripped_value = attr.value.strip() if attr.value else ''
    if is_code_expression(stripped_value):
        body = parse_expression(stripped_value)[1]
        parameters = node_globals.to_dictionary() if node_globals else {}
        return Expression(body).execute(parameters)
    return attr.value
