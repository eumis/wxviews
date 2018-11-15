'''Rendering pipeline for WxNode'''
# pylint: disable=W0613

from pyviews import RenderingPipeline
from pyviews.core.xml import XmlAttr
from pyviews.core.observable import InheritedDict
from pyviews.core.compilation import Expression
from pyviews.rendering.expression import is_code_expression, parse_expression
from pyviews.rendering.pipeline import apply_attributes
from wxviews.core.node import WxNode

def get_wx_pipeline() -> RenderingPipeline:
    '''Returns rendering pipeline for WxNode'''
    return RenderingPipeline(steps=[
        init_instance,
        setup_setter,
        apply_attributes
    ])

def init_instance(node: WxNode, instance_type: type = None, parent=None, **args):
    '''Creates instance and sets it to node'''
    init_attrs = [attr for attr in node.xml_node.children if attr.namespace == 'init']
    kwargs = {attr.name: _get_init_value(attr, node.node_globals) for attr in init_attrs}
    instance = instance_type(parent, **kwargs)
    node.init(instance)

def _get_init_value(attr: XmlAttr, node_globals: InheritedDict):
    stripped_value = attr.value.strip() if attr.value else ''
    if is_code_expression(stripped_value):
        body = parse_expression(stripped_value)[1]
        return Expression(body).execute(node_globals.to_dictionary())
    return attr.value

def setup_setter(node: WxNode, **args):
    '''Sets attr_setter for WxNode'''
    node.attr_setter = _wx_setter

def _wx_setter(node: WxNode, key, value):
    if key in node.properties:
        node.properties[key].set(value)
    elif hasattr(node, key):
        setattr(node, key, value)
    elif hasattr(node.instance, key):
        setattr(node.instance, key, value)
