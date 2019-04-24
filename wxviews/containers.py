"""Contains methods for node setups creation"""
from pyviews.core import Node, XmlNode
from pyviews.rendering import RenderingPipeline
from pyviews.core.observable import InheritedDict
from pyviews.rendering import apply_attributes, render_children
from pyviews.rendering import render_view
from pyviews.container import render


class Container(Node):
    """Used to combine some xml elements"""


def get_container_pipeline() -> RenderingPipeline:
    """Returns setup for container"""
    return RenderingPipeline(steps=[
        apply_attributes,
        render_container_children
    ])


def render_container_children(node, **args):
    """Renders container children"""
    render_children(node, **_get_child_args(node, **args))


def _get_child_args(node: Container, parent=None, sizer=None, **_):
    return {
        'parent_node': node,
        'parent': parent,
        'node_globals': InheritedDict(node.node_globals),
        'sizer': sizer
    }


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
    return RenderingPipeline(steps=[
        apply_attributes,
        render_view_children,
        rerender_on_view_change
    ])


def render_view_children(node: View, **args):
    """Finds view by name attribute and renders it as view node child"""
    if node.name:
        child_args = _get_child_args(node, **args)
        content = render_view(node.name, **child_args)
        node.add_child(content)


def rerender_on_view_change(node: View, **args):
    """Subscribes to name change and renders new view"""
    node.name_changed = lambda n, val, old, a=args: _rerender_view(n, a) \
        if _is_different(val, old) else None


def _is_different(one: str, two: str):
    empty_values = [None, '']
    return one != two and \
           not (one in empty_values and two in empty_values)


def _rerender_view(node: View, args: dict):
    node.destroy_children()
    render_view_children(node, **args)
    if 'parent' in args:
        args['parent'].Layout()


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
    return RenderingPipeline(steps=[
        apply_attributes,
        render_for_items,
        rerender_on_items_change
    ])


def render_for_items(node: For, **args):
    """Renders For children"""
    _render_for_children(node, node.items, **args)


def _render_for_children(node: For, items: list, index_shift=0, **args):
    item_xml_nodes = node.xml_node.children
    for index, item in enumerate(items):
        for xml_node in item_xml_nodes:
            child_args = _get_for_child_args(node, index + index_shift, item, **args)
            child = render(xml_node, **child_args)
            node.add_child(child)


def _get_for_child_args(node: For, index, item, **args):
    child_args = _get_child_args(node, **args)
    child_globals = child_args['node_globals']
    child_globals['index'] = index
    child_globals['item'] = item
    return child_args


def rerender_on_items_change(node: For, **args):
    """Subscribes to items change and updates children"""
    node.items_changed = lambda n, v, o, a=args: _on_items_changed(n, **a) \
        if v != o else None


def _on_items_changed(node: For, parent=None, **_):
    _destroy_overflow(node)
    _update_existing(node)
    _create_not_existing(node)
    if parent:
        parent.Layout()


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


def _create_not_existing(node: For):
    item_children_count = len(node.xml_node.children)
    start = int(len(node.children) / item_children_count)
    end = len(node.items)
    items = [node.items[i] for i in range(start, end)]
    _render_for_children(node, items, start)


def get_if_pipeline() -> RenderingPipeline:
    """Returns setup for For node"""
    return RenderingPipeline(steps=[
        apply_attributes,
        render_if,
        rerender_on_condition_change
    ])


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


def render_if(node: If, **args):
    """Renders children nodes if condition is true"""
    if node.condition:
        render_children(node, **_get_child_args(node, **args))


def rerender_on_condition_change(node: If, **args):
    """Rerenders if on condition change"""
    node.condition_changed = lambda n, v, o: _on_condition_change(n, v, o, **args)


def _on_condition_change(node: If, val: bool, old: bool, parent=None, **args):
    if val == old:
        return
    node.destroy_children()
    render_if(node, **args)
    if parent:
        parent.Layout()
