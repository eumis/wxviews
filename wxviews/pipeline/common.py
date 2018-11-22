'''Common pipeline functionality'''

# pylint: disable=W0613

from pyviews.core.node import InstanceNode
from pyviews.rendering.pipeline import apply_attribute

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
