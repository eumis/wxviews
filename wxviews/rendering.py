'''Customizing of wx parsing'''

from wx import Sizer, GridSizer, MenuBar, Menu # pylint: disable=E0611
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.observable import InheritedDict
from pyviews.core.compilation import Expression
from pyviews.core.node import Node
from pyviews.rendering.expression import is_code_expression, parse_expression
from pyviews.rendering.node import get_inst_type, get_init_args
from wxviews.core.node import WxNode
from wxviews.core.sizers import SizerNode

def create_node(xml_node: XmlNode,
                parent=None,
                node_globals: InheritedDict = None,
                sizer=None,
                **init_args) -> Node:
    '''Creates node from xml node using namespace as module and tag name as class name'''
    inst_type = get_inst_type(xml_node)
    if issubclass(inst_type, Node):
        args = {**init_args, **{'xml_node': xml_node}}
        if parent is not None:
            args['parent'] = parent
        if node_globals is not None:
            args['node_globals'] = node_globals
        return _create_inst(inst_type, **args)
    elif issubclass(inst_type, GridSizer):
        args = _get_attr_args_values(xml_node, 'init', node_globals)
        inst = inst_type(*args)
        return SizerNode(inst, xml_node, node_globals=node_globals)
    elif issubclass(inst_type, Sizer):
        args = get_attr_args(xml_node, 'init', node_globals)
        inst = inst_type(**args)
        return SizerNode(inst, xml_node, node_globals=node_globals, parent=parent, sizer=sizer)
    elif issubclass(inst_type, MenuBar) or issubclass(inst_type, Menu):
        return WxNode(inst_type(), xml_node, node_globals=node_globals)
    else:
        args = get_attr_args(xml_node, 'init', node_globals)
        inst = inst_type(parent, **args)
        return WxNode(inst, xml_node, node_globals=node_globals)

def _create_inst(inst_type, **init_args):
    '''Creates class instance with args'''
    args, kwargs = get_init_args(inst_type, init_args, True)
    return inst_type(*args, **kwargs)

def _get_attr_args_values(xml_node, namespace: str, node_globals: InheritedDict = None) -> dict:
    init_attrs = [attr for attr in xml_node.attrs if attr.namespace == namespace]
    return [_get_init_value(attr, node_globals) for attr in init_attrs]

def get_attr_args(xml_node, namespace: str, node_globals: InheritedDict = None) -> dict:
    '''Returs args from attributes with provided namespace'''
    init_attrs = [attr for attr in xml_node.attrs if attr.namespace == namespace]
    return {attr.name: _get_init_value(attr, node_globals) for attr in init_attrs}

def _get_init_value(attr: XmlAttr, node_globals: InheritedDict):
    stripped_value = attr.value.strip() if attr.value else ''
    if is_code_expression(stripped_value):
        body = parse_expression(stripped_value)[1]
        parameters = node_globals.to_dictionary() if node_globals else {}
        return Expression(body).execute(parameters)
    return attr.value
