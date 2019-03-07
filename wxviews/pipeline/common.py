'''Common pipeline functionality'''

# pylint: disable=W0613

from pyviews.core.node import InstanceNode
from pyviews.rendering.pipeline import apply_attribute
from wxviews.core import WxNode
from wxviews.rendering import get_attr_args

def setup_instance_node_setter(node: WxNode, **args):
    '''Sets attr_setter for WxNode'''
    node.attr_setter = instance_node_setter

def instance_node_setter(node: InstanceNode, key, value):
    '''Sets default wxviews attr_setter'''
    if key in node.properties:
        node.properties[key].set(value)
    elif hasattr(node, key):
        setattr(node, key, value)
    elif hasattr(node.instance, key):
        setattr(node.instance, key, value)

def apply_attributes(node: InstanceNode, **args):
    '''Applies attributes for node'''
    attrs = [attr for attr in node.xml_node.attrs if attr.namespace not in ['init', 'sizer']]
    for attr in attrs:
        apply_attribute(node, attr)

def add_to_sizer(node: WxNode, sizer=None, **args):
    '''Adds to wx instance to sizer'''
    if sizer is None:
        return
    args = get_attr_args(node.xml_node, 'sizer', node.node_globals)
    sizer.Add(node.instance, **args)
