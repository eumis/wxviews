"""Customizing of wx parsing"""
from injectool import resolve
from pyviews.core import Node
from pyviews.expression import is_expression, parse_expression, Expression
from pyviews.rendering import get_type
from pyviews.rendering.pipeline import _get_init_args

from wx import Sizer, GridSizer, MenuBar, Menu, StaticBoxSizer
from pyviews.core.xml import XmlNode, XmlAttr
from pyviews.core.observable import InheritedDict

from wxviews.core import WxRenderingContext
from wxviews.sizers import SizerNode
from wxviews.widgets import WidgetNode


def create_node(xml_node: XmlNode, context: WxRenderingContext) -> Node:
    """Creates node from xml node using namespace as module and tag name as class name"""
    inst_type = get_type(xml_node)
    if issubclass(inst_type, Node):
        args = {**context, **{'xml_node': xml_node}}
        if context.parent is not None:
            args['parent'] = context.parent
        if context.node_globals is not None:
            args['node_globals'] = context.node_globals
        return _create_inst(inst_type, **args)
    if issubclass(inst_type, GridSizer):
        args = _get_attr_args_values(xml_node, 'init', context.node_globals)
        inst = inst_type(*args)
        return SizerNode(inst, xml_node, node_globals=context.node_globals)
    if issubclass(inst_type, StaticBoxSizer):
        init_args = get_attr_args(xml_node, 'init', context.node_globals)
        args = []
        try:
            static_box = init_args.pop('box')
            args.append(static_box)
        except KeyError:
            args.append(init_args.pop('orient'))
            args.append(context.parent)
        inst = inst_type(*args, **init_args)
        return SizerNode(inst, xml_node,
                         node_globals=context.node_globals,
                         parent=inst.GetStaticBox(),
                         sizer=context.sizer)
    if issubclass(inst_type, Sizer):
        args = get_attr_args(xml_node, 'init', context.node_globals)
        inst = inst_type(**args)
        return SizerNode(inst, xml_node,
                         node_globals=context.node_globals,
                         parent=context.parent,
                         sizer=context.sizer)
    if issubclass(inst_type, MenuBar) or issubclass(inst_type, Menu):
        return WidgetNode(inst_type(), xml_node, node_globals=context.node_globals)

    args = get_attr_args(xml_node, 'init', context.node_globals)
    inst = inst_type(context.parent, **args)
    return WidgetNode(inst, xml_node, node_globals=context.node_globals)


def _create_inst(inst_type, **init_args):
    """Creates class instance with args"""
    args, kwargs = _get_init_args(inst_type, init_args, True)
    return inst_type(*args, **kwargs)


def _get_attr_args_values(xml_node, namespace: str, node_globals: InheritedDict = None) -> list:
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
        return resolve(Expression, body).execute(parameters)
    return attr.value
