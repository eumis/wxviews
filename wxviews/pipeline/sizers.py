'''Rendering pipeline for SizerNode'''

# pylint: disable=W0613

from wx import FlexGridSizer # pylint: disable=E0611
from pyviews.core import InheritedDict
from pyviews.rendering import RenderingPipeline, render_children
from wxviews.node import SizerNode, GrowableRow, GrowableCol
from .common import instance_node_setter, apply_attributes, add_to_sizer

def get_sizer_pipeline() -> RenderingPipeline:
    '''Returns rendering pipeline for SizerNode'''
    return RenderingPipeline(steps=[
        setup_setter,
        apply_attributes,
        add_to_sizer,
        render_sizer_children,
        set_sizer_to_parent
    ])

def setup_setter(node: SizerNode, **args):
    '''Sets attr_setter for SizerNode'''
    node.attr_setter = instance_node_setter

def render_sizer_children(node: SizerNode, parent=None, **args):
    '''Renders sizer children'''
    render_children(node,
                    parent_node=node,
                    parent=parent,
                    node_globals=InheritedDict(node.node_globals),
                    sizer=node.instance)

def set_sizer_to_parent(node, parent=None, sizer=None, **args):
    '''Pass sizer to parent SetSizer'''
    if parent is not None and sizer is None:
        parent.SetSizer(node.instance, True)

def get_growable_row_pipeline() -> RenderingPipeline:
    '''Returns rendering pipeline for GrowableRow'''
    return RenderingPipeline(steps=[
        apply_attributes,
        add_growable_row_to_sizer
    ])

def add_growable_row_to_sizer(node: GrowableRow, sizer: FlexGridSizer, **args):
    '''Calls AddGrowableRow for sizer'''
    sizer.AddGrowableRow(node.idx, node.proportion)

def get_growable_col_pipeline() -> RenderingPipeline:
    '''Returns rendering pipeline for GrowableRow'''
    return RenderingPipeline(steps=[
        apply_attributes,
        add_growable_col_to_sizer
    ])

def add_growable_col_to_sizer(node: GrowableCol, sizer: FlexGridSizer, **args):
    '''Calls AddGrowableCol for sizer'''
    sizer.AddGrowableCol(node.idx, node.proportion)
