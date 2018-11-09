''''''

from pyviews import RenderingPipeline
from pyviews.rendering.pipeline import apply_attributes
from wxviews.core.node import WxNode

def get_wx_pipeline():
    return RenderingPipeline(steps=[
        setup_setter,
        apply_attributes
    ])

def setup_setter(node: WxNode, **args):
    node.attr_setter = _wx_setter

def _wx_setter(node: WxNode, key, value):
    if key in node.properties:
        node.properties[key].set(value)
    elif hasattr(node, key):
        setattr(node, key, value)
    elif hasattr(node.instance, key):
        setattr(node.instance, key, value)
    else:
        node.instance.configure(**{key:value})
