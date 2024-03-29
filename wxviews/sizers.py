"""Rendering pipeline for SizerNode"""

from typing import Any, Optional

from pyviews.core.rendering import InstanceNode, Node, NodeGlobals
from pyviews.core.xml import XmlNode
from pyviews.pipes import render_children
from pyviews.rendering.pipeline import RenderingPipeline, get_type
from wx import GridSizer, Sizer, StaticBoxSizer

from wxviews.core.node import Sizerable
from wxviews.core.pipes import add_to_sizer, apply_attributes
from wxviews.core.rendering import WxRenderingContext, get_attr_args, get_init_value


class SizerNode(InstanceNode, Sizerable):
    """Wrapper under sizer"""

    def __init__(
        self,
        instance: Sizer,
        xml_node: XmlNode,
        node_globals: Optional[NodeGlobals] = None,
        parent = None,
        sizer = None
    ):
        InstanceNode.__init__(self, instance, xml_node, node_globals = node_globals)
        Sizerable.__init__(self)
        self._parent = parent
        self._parent_sizer = sizer

    @property
    def sizer_item(self) -> Any:
        return self._instance

    def destroy(self):
        super().destroy()
        if self._parent_sizer is None and self._parent is not None:
            self._parent.SetSizer(None, True)


def get_sizer_pipeline() -> RenderingPipeline:
    """Returns rendering pipeline for SizerNode"""
    return RenderingPipeline(
        pipes = [apply_attributes, add_to_sizer, render_sizer_children, set_sizer_to_parent],
        create_node = _create_sizer_node,
        name = 'sizer pipeline'
    )


def _create_sizer_node(context: WxRenderingContext) -> SizerNode:
    inst_type = get_type(context.xml_node)
    if issubclass(inst_type, GridSizer):
        args = _get_init_values(context.xml_node, context.node_globals)
        inst = inst_type(*args)
        return SizerNode(inst, context.xml_node, node_globals = context.node_globals)

    if issubclass(inst_type, StaticBoxSizer):
        init_args = get_attr_args(context.xml_node, 'init', context.node_globals)
        args = []
        try:
            static_box = init_args.pop('box')
            args.append(static_box)
        except KeyError:
            args.append(init_args.pop('orient'))
            args.append(context.parent)
        inst = inst_type(*args, **init_args)
        return SizerNode(
            inst,
            context.xml_node,
            node_globals = context.node_globals,
            parent = inst.GetStaticBox(),
            sizer = context.sizer
        )
    args = get_attr_args(context.xml_node, 'init', context.node_globals)
    inst = inst_type(**args)
    return SizerNode(
        inst, context.xml_node, node_globals = context.node_globals, parent = context.parent, sizer = context.sizer
    )


def _get_init_values(xml_node: XmlNode, node_globals: Optional[NodeGlobals] = None) -> list:
    init_attrs = [attr for attr in xml_node.attrs if attr.namespace == 'init']
    return [get_init_value(attr, node_globals) for attr in init_attrs]


def render_sizer_children(node: SizerNode, context: WxRenderingContext):
    """Renders sizer children"""
    render_children(
        node,
        context,
        lambda x,
        n,
        ctx: WxRenderingContext({
            'parent_node': n,
            'parent': ctx.parent,
            'node_globals': NodeGlobals(node.node_globals),
            'sizer': node.instance,
            'xml_node': x
        })
    )


def set_sizer_to_parent(node, context: WxRenderingContext):
    """Pass sizer to parent SetSizer"""
    if context.parent is not None and context.sizer is None:
        context.parent.SetSizer(node.instance, True)


class GrowableRow(Node):
    """Represents FlexGridSizer.AddGrowableRow method"""

    def __init__(self, xml_node: XmlNode, node_globals: Optional[NodeGlobals] = None):
        super().__init__(xml_node, node_globals = node_globals)
        self.idx = None
        self.proportion = 0


def get_growable_row_pipeline() -> RenderingPipeline:
    """Returns rendering pipeline for GrowableRow"""
    return RenderingPipeline(pipes = [apply_attributes, add_growable_row_to_sizer], name = 'growable row pipeline')


def add_growable_row_to_sizer(node: GrowableRow, context: WxRenderingContext):
    """Calls AddGrowableRow for sizer"""
    context.sizer.AddGrowableRow(node.idx, node.proportion)


class GrowableCol(Node):
    """Represents FlexGridSizer.AddGrowableRow method"""

    def __init__(self, xml_node: XmlNode, node_globals: Optional[NodeGlobals] = None):
        super().__init__(xml_node, node_globals = node_globals)
        self.idx = None
        self.proportion = 0


def get_growable_col_pipeline() -> RenderingPipeline:
    """Returns rendering pipeline for GrowableRow"""
    return RenderingPipeline(pipes = [apply_attributes, add_growable_col_to_sizer], name = 'growable col pipeline')


def add_growable_col_to_sizer(node: GrowableCol, context: WxRenderingContext):
    """Calls AddGrowableCol for sizer"""
    context.sizer.AddGrowableCol(node.idx, node.proportion)


def set_sizer(node: Sizerable, key: str, value: Any):
    """Sets sizer argument"""
    if key == '':
        node.sizer_args = {**node.sizer_args, **value}
    else:
        node.sizer_args[key] = value
