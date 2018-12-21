'''Rendering pipeline for WxNode'''

# pylint: disable=W0613

from wx import Frame # pylint: disable=E0611
from pyviews import RenderingPipeline, InstanceNode
from pyviews.rendering.pipeline import render_children
from wxviews.pipeline.common import setup_instance_node_setter, apply_attributes

def get_menu_bar_pipeline():
    '''Return render pipeline for MenuBar'''
    return RenderingPipeline(steps=[
        setup_instance_node_setter,
        apply_attributes,
        render_children,
        set_to_frame
    ])

def set_to_frame(node: InstanceNode, parent: Frame = None, **args):
    '''Sets menu bar for parent Frame'''
    if not isinstance(parent, Frame):
        msg = 'parent for MenuBar should be Frame, but it is {0}'.format(parent)
        raise TypeError(msg)
    parent.SetMenuBar(node.instance)
