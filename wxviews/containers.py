"""Contains methods for node setups creation"""
from typing import Any

from pyviews.core import Node, XmlNode
from pyviews.pipes import render_children
from pyviews.rendering import RenderingPipeline, render
from pyviews.core.observable import InheritedDict
from pyviews.rendering.views import render_view

from wxviews.core import WxRenderingContext, apply_attributes


class Container(Node):
    """Used to combine some xml elements"""


def get_container_pipeline() -> RenderingPipeline:
    """Returns setup for container"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        render_container_children
    ])


def render_container_children(node, context: WxRenderingContext):
    """Renders container children"""
    render_children(node, context, _get_child_context)


def _get_child_context(xml_node: XmlNode, parent_node: Container,
                       context: WxRenderingContext) -> WxRenderingContext:
    return WxRenderingContext({
        'parent_node': parent_node,
        'parent': context.parent,
        'node_globals': InheritedDict(parent_node.node_globals),
        'sizer': context.sizer,
        'xml_node': xml_node
    })


class View(Container):
    """Loads xml from another file"""

    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(xml_node, node_globals=node_globals)
        self._name = None
        self.name_changed = lambda view, name, previous_name: None

    @property
    def name(self):
        """Returns view name"""
        return self._name

    @name.setter
    def name(self, value):
        old_name = self._name
        self._name = value
        self.name_changed(self, value, old_name)


def get_view_pipeline() -> RenderingPipeline:
    """Returns setup for container"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        render_view_content,
        rerender_on_view_change
    ])


def render_view_content(node: View, context: WxRenderingContext):
    """Finds view by name attribute and renders it as view node child"""
    if node.name:
        child_context = _get_child_context(node.xml_node, node, context)
        content = render_view(node.name, child_context)
        node.add_child(content)


def rerender_on_view_change(node: View, context: WxRenderingContext):
    """Subscribes to name change and renders new view"""
    node.name_changed = lambda n, val, old: _rerender_view(n, context) \
        if _is_different(val, old) else None


def _is_different(one: str, two: str):
    empty_values = [None, '']
    return one != two and not (one in empty_values and two in empty_values)


def _rerender_view(node: View, context: WxRenderingContext):
    node.destroy_children()
    render_view_content(node, context)
    if context.parent:
        context.parent.Layout()


class For(Container):
    """Renders children for every item in items collection"""

    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(xml_node, node_globals=node_globals)
        self._items = []
        self.items_changed = lambda node, items, old_items: None

    @property
    def items(self):
        """Returns items"""
        return self._items

    @items.setter
    def items(self, value):
        old_items = self._items
        self._items = value
        self.items_changed(self, value, old_items)


def get_for_pipeline() -> RenderingPipeline:
    """Returns setup for For node"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        render_for_items,
        rerender_on_items_change
    ])


def render_for_items(node: For, context: WxRenderingContext):
    """Renders For children"""
    _render_for_children(node, node.items, context)


def _render_for_children(node: For, items: list, context: WxRenderingContext, index_shift=0):
    item_xml_nodes = node.xml_node.children
    for index, item in enumerate(items):
        for xml_node in item_xml_nodes:
            child_context = _get_for_child_args(xml_node, index + index_shift, item, node, context)
            child = render(child_context)
            node.add_child(child)


def _get_for_child_args(xml_node: XmlNode, index: int, item: Any,
                        parent_node: For, context: WxRenderingContext):
    child_context = _get_child_context(xml_node, parent_node, context)
    child_globals = child_context.node_globals
    child_globals['index'] = index
    child_globals['item'] = item
    return child_context


def rerender_on_items_change(node: For, context: WxRenderingContext):
    """Subscribes to items change and updates children"""
    node.items_changed = lambda n, v, o: _on_items_changed(n, context) \
        if v != o else None


def _on_items_changed(node: For, context: WxRenderingContext):
    _destroy_overflow(node)
    _update_existing(node)
    _create_not_existing(node, context)
    if context.parent:
        context.parent.Layout()


def _destroy_overflow(node: For):
    try:
        items_count = len(node.items)
        children_count = len(node.xml_node.children) * items_count
        overflow = node.children[children_count:]
        for child in overflow:
            child.destroy()
        node._children = node.children[:children_count]
    except IndexError:
        pass


def _update_existing(node: For):
    item_children_count = len(node.xml_node.children)
    try:
        for index, item in enumerate(node.items):
            start = index * item_children_count
            end = (index + 1) * item_children_count
            for child_index in range(start, end):
                globs = node.children[child_index].node_globals
                globs['item'] = item
                globs['index'] = index
    except IndexError:
        pass


def _create_not_existing(node: For, context: WxRenderingContext):
    item_children_count = len(node.xml_node.children)
    start = int(len(node.children) / item_children_count)
    end = len(node.items)
    items = [node.items[i] for i in range(start, end)]
    _render_for_children(node, items, context, start)


class If(Container):
    """Renders children if condition is True"""

    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(xml_node, node_globals=node_globals)
        self._condition = False
        self.condition_changed = lambda node, cond, old_cond: None

    @property
    def condition(self):
        """Returns condition"""
        return self._condition

    @condition.setter
    def condition(self, value):
        old_condition = self._condition
        self._condition = value
        self.condition_changed(self, value, old_condition)


def get_if_pipeline() -> RenderingPipeline:
    """Returns setup for For node"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        render_if,
        rerender_on_condition_change
    ])


def render_if(node: If, context: WxRenderingContext):
    """Renders children nodes if condition is true"""
    if node.condition:
        render_children(node, context, _get_child_context)


def rerender_on_condition_change(node: If, context: WxRenderingContext):
    """Rerenders if on condition change"""
    node.condition_changed = lambda n, v, o: _on_condition_change(n, v, o, context)


def _on_condition_change(node: If, val: bool, old: bool, context: WxRenderingContext):
    if val == old:
        return
    node.destroy_children()
    render_if(node, context)
    if context.parent:
        context.parent.Layout()
