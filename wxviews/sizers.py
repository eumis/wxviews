"""Rendering pipeline for SizerNode"""
from typing import Any

from wx import FlexGridSizer, Sizer
from pyviews.core import InheritedDict, InstanceNode, Node, XmlNode
from pyviews.rendering import RenderingPipeline, render_children

from wxviews.core import Sizerable
from wxviews.core.pipeline import instance_node_setter, apply_attributes, add_to_sizer


class SizerNode(InstanceNode, Sizerable):
    """Wrapper under sizer"""

    def __init__(self, instance: Sizer, xml_node: XmlNode,
                 node_globals: InheritedDict = None, parent=None, sizer=None):
        super().__init__(instance, xml_node, node_globals=node_globals)
        self._parent = parent
        self._parent_sizer = sizer
        self._sizer_args: dict = {}

    @property
    def sizer_args(self) -> dict:
        return self._sizer_args

    @sizer_args.setter
    def sizer_args(self, value):
        self._sizer_args = value

    def destroy(self):
        super().destroy()
        if self._parent_sizer is None and self._parent is not None:
            self._parent.SetSizer(None, True)


def get_sizer_pipeline() -> RenderingPipeline:
    """Returns rendering pipeline for SizerNode"""
    return RenderingPipeline(steps=[
        setup_setter,
        apply_attributes,
        add_to_sizer,
        render_sizer_children,
        set_sizer_to_parent
    ])


def setup_setter(node: SizerNode, **_):
    """Sets attr_setter for SizerNode"""
    node.attr_setter = instance_node_setter


def render_sizer_children(node: SizerNode, parent=None, **_):
    """Renders sizer children"""
    render_children(node,
                    parent_node=node,
                    parent=parent,
                    node_globals=InheritedDict(node.node_globals),
                    sizer=node.instance)


def set_sizer_to_parent(node, parent=None, sizer=None, **_):
    """Pass sizer to parent SetSizer"""
    if parent is not None and sizer is None:
        parent.SetSizer(node.instance, True)


class GrowableRow(Node):
    """Represents FlexGridSizer.AddGrowableRow method"""

    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(xml_node, node_globals=node_globals)
        self.idx = None
        self.proportion = 0


def get_growable_row_pipeline() -> RenderingPipeline:
    """Returns rendering pipeline for GrowableRow"""
    return RenderingPipeline(steps=[
        apply_attributes,
        add_growable_row_to_sizer
    ])


def add_growable_row_to_sizer(node: GrowableRow, sizer: FlexGridSizer, **_):
    """Calls AddGrowableRow for sizer"""
    sizer.AddGrowableRow(node.idx, node.proportion)


class GrowableCol(Node):
    """Represents FlexGridSizer.AddGrowableRow method"""

    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(xml_node, node_globals=node_globals)
        self.idx = None
        self.proportion = 0


def get_growable_col_pipeline() -> RenderingPipeline:
    """Returns rendering pipeline for GrowableRow"""
    return RenderingPipeline(steps=[
        apply_attributes,
        add_growable_col_to_sizer
    ])


def add_growable_col_to_sizer(node: GrowableCol, sizer: FlexGridSizer, **_):
    """Calls AddGrowableCol for sizer"""
    sizer.AddGrowableCol(node.idx, node.proportion)


def sizer(node: Sizerable, key: str, value: Any):
    """Sets sizer argument"""
    if key == '':
        node.sizer_args = {**node.sizer_args, **value}
    else:
        node.sizer_args[key] = value
