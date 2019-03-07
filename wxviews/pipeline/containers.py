'''Contains methods for node setups creation'''

# pylint: disable=W0613

from pyviews.rendering import RenderingPipeline
from pyviews.core.observable import InheritedDict
from pyviews.rendering import apply_attributes, render_children
from pyviews.rendering import render_view
from pyviews.container import render
from wxviews.node import Container, View, For, If

def get_container_pipeline() -> RenderingPipeline:
    '''Returns setup for container'''
    return RenderingPipeline(steps=[
        apply_attributes,
        render_container_children
    ])

def render_container_children(node, **args):
    '''Renders container children'''
    render_children(node, **_get_child_args(node, **args))

def _get_child_args(node: Container, parent=None, sizer=None, **args):
    return {
        'parent_node': node,
        'parent': parent,
        'node_globals': InheritedDict(node.node_globals),
        'sizer': sizer
    }



def get_view_pipeline() -> RenderingPipeline:
    '''Returns setup for container'''
    return RenderingPipeline(steps=[
        apply_attributes,
        render_view_children,
        rerender_on_view_change
    ])

def render_view_children(node: View, **args):
    '''Finds view by name attribute and renders it as view node child'''
    if node.name:
        child_args = _get_child_args(node, **args)
        content = render_view(node.name, **child_args)
        node.set_content(content)

def rerender_on_view_change(node: View, **args):
    '''Subscribes to name change and renders new view'''
    node.name_changed = lambda n, val, old, a=args: _rerender_view(n, a) \
                                    if _is_different(val, old) else None

def _is_different(one: str, two: str):
    empty_values = [None, '']
    return one != two and\
           not (one in empty_values and two in empty_values)

def _rerender_view(node: View, args: dict):
    node.destroy_children()
    render_view_children(node, **args)
    if 'parent' in args:
        args['parent'].Layout()



def get_for_pipeline() -> RenderingPipeline:
    '''Returns setup for For node'''
    return RenderingPipeline(steps=[
        apply_attributes,
        render_for_items,
        rerender_on_items_change
    ])

def render_for_items(node: For, **args):
    '''Renders For children'''
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
    '''Subscribes to items change and updates children'''
    node.items_changed = lambda n, v, o, a=args: _on_items_changed(n, **a) \
                                     if v != o else None

def _on_items_changed(node: For, parent=None, **args):
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
        node._children = node.children[:children_count] # pylint: disable=W0212
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
    '''Returns setup for For node'''
    return RenderingPipeline(steps=[
        apply_attributes,
        render_if,
        rerender_on_condition_change
    ])

def render_if(node: If, **args):
    '''Renders children nodes if condition is true'''
    if node.condition:
        render_children(node, **_get_child_args(node, **args))

def rerender_on_condition_change(node: If, **args):
    '''Rerenders if on condition change'''
    node.condition_changed = lambda n, v, o: _on_condition_change(n, v, o, **args)

def _on_condition_change(node: If, val: bool, old: bool, parent=None, **args):
    if val == old:
        return
    node.destroy_children()
    render_if(node, **args)
    if parent:
        parent.Layout()
