'''Rendering pipeline for SizerNode'''

# pylint: disable=W0613

from pyviews import RenderingPipeline, Node
from wxviews.pipeline.common import apply_attributes
from wxviews.core.call import Call

def get_call_pipeline() -> RenderingPipeline:
    '''Returns pipeline for Call node'''
    return RenderingPipeline(steps=[
        set_attrs_setter,
        apply_attributes,
        apply_call
    ])

def set_attrs_setter(node: Call, **args):
    '''Sets attr_setter for WxNode'''
    node.attr_setter = _call_attr_setter

def _call_attr_setter(node: Call, key: str, value):
    '''Sets Call attr_setter'''
    if key in node.properties:
        node.properties[key].set(value)
    elif hasattr(node, key):
        setattr(node, key, value)
    elif key.startswith('*'):
        node.add_kwarg(key[1:], value)
    else:
        node.add_arg(value)

def apply_call(node: Call, parent_node: Node = None, **args):
    '''Applies call'''
    try:
        method = getattr(parent_node.instance, node.method)
    except AttributeError:
        method = getattr(parent_node, node.method)
    args, kwargs = node.get_args()
    method(*args, **kwargs)
