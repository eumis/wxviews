"""Customizing of wx parsing"""

from wx import Sizer, GridSizer, MenuBar, Menu, StaticBoxSizer
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.observable import InheritedDict
from pyviews.core.node import Node
from pyviews.compilation import is_expression, parse_expression
from pyviews.rendering import get_inst_type, get_init_args
from pyviews.container import expression

from wxviews.sizers import SizerNode
from wxviews.widgets import WidgetNode


def create_node(xml_node: XmlNode,
                parent=None,
                node_globals: InheritedDict = None,
                sizer=None,
                **init_args) -> Node:
    """Creates node from xml node using namespace as module and tag name as class name"""
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
    elif issubclass(inst_type, StaticBoxSizer):
        init_args = get_attr_args(xml_node, 'init', node_globals)
        args = []
        try:
            static_box = init_args.pop('box')
            args.append(static_box)
        except KeyError:
            args.append(init_args.pop('orient'))
            args.append(parent)
        inst = inst_type(*args, **init_args)
        return SizerNode(inst, xml_node, node_globals=node_globals, parent=inst.GetStaticBox(), sizer=sizer)
    elif issubclass(inst_type, Sizer):
        args = get_attr_args(xml_node, 'init', node_globals)
        inst = inst_type(**args)
        return SizerNode(inst, xml_node, node_globals=node_globals, parent=parent, sizer=sizer)
    elif issubclass(inst_type, MenuBar) or issubclass(inst_type, Menu):
        return WidgetNode(inst_type(), xml_node, node_globals=node_globals)
    else:
        args = get_attr_args(xml_node, 'init', node_globals)
        inst = inst_type(parent, **args)
        return WidgetNode(inst, xml_node, node_globals=node_globals)


def _create_inst(inst_type, **init_args):
    """Creates class instance with args"""
    args, kwargs = get_init_args(inst_type, init_args, True)
    return inst_type(*args, **kwargs)


def _get_attr_args_values(xml_node, namespace: str, node_globals: InheritedDict = None) -> dict:
    init_attrs = [attr for attr in xml_node.attrs if attr.namespace == namespace]
    return [_get_init_value(attr, node_globals) for attr in init_attrs]


def get_attr_args(xml_node, namespace: str, node_globals: InheritedDict = None) -> dict:
    """Returns args from attributes with provided namespace"""
    init_attrs = [attr for attr in xml_node.attrs if attr.namespace == namespace]
    args = {}
    for attr in init_attrs:
        value = _get_init_value(attr, node_globals)
        if attr.name == '':
            args = {**args, **value}
        else:
            args[attr.name] = value
    return args


def _get_init_value(attr: XmlAttr, node_globals: InheritedDict):
    stripped_value = attr.value.strip() if attr.value else ''
    if is_expression(stripped_value):
        body = parse_expression(stripped_value)[1]
        parameters = node_globals.to_dictionary() if node_globals else {}
        return expression(body).execute(parameters)
    return attr.value
