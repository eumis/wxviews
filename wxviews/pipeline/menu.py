'''Rendering pipeline for WxNode'''

# pylint: disable=W0613

from wx import Frame, MenuBar # pylint: disable=E0611
from pyviews import RenderingPipeline, InstanceNode, Property
from pyviews.core.observable import InheritedDict
from pyviews.rendering.pipeline import render_children
from wxviews.pipeline.common import setup_instance_node_setter, apply_attributes

def get_menu_bar_pipeline():
    '''Return render pipeline for MenuBar'''
    return RenderingPipeline(steps=[
        setup_instance_node_setter,
        apply_attributes,
        render_menu_children,
        set_to_frame
    ])

def render_menu_children(node: InstanceNode, **args):
    '''Renders sizer children'''
    render_children(node,
                    parent_node=node,
                    node_globals=InheritedDict(node.node_globals))

def set_to_frame(node: InstanceNode, parent: Frame = None, **args):
    '''Sets menu bar for parent Frame'''
    if not isinstance(parent, Frame):
        msg = 'parent for MenuBar should be Frame, but it is {0}'.format(parent)
        raise TypeError(msg)
    parent.SetMenuBar(node.instance)

def get_menu_pipeline():
    '''Return render pipeline for Menu'''
    return RenderingPipeline(steps=[
        setup_instance_node_setter,
        apply_attributes,
        render_menu_children,
        set_to_menu_bar
    ])

def add_menu_properties(node: InstanceNode, **args):
    '''Adds menu specific properties to node'''
    node.properties['title'] = Property('title')

def set_to_menu_bar(node: InstanceNode, parent: MenuBar = None, **args):
    '''Sets menu for parent MenuBar'''
    if not isinstance(parent, MenuBar):
        msg = 'parent for Menu should be MenuBar, but it is {0}'.format(parent)
        raise TypeError(msg)
    parent.Append(node.instance, node.title)