"""Contains rendering steps for style nodes"""

from pyviews.core import XmlAttr, InheritedDict, Node
from pyviews.compilation import is_expression, parse_expression
from pyviews.rendering import get_setter, render_children, RenderingPipeline, apply_attributes
from pyviews.container import expression
from wxviews.node import Style, StyleItem, StyleError
from wxviews.node.styles import StylesView
from wxviews.pipeline.containers import render_view_children


def get_style_pipeline() -> RenderingPipeline:
    """Returns pipeline for style node"""
    node_setup = RenderingPipeline()
    node_setup.steps = [
        setup_node_styles,
        apply_style_items,
        apply_parent_items,
        store_to_node_styles,
        render_child_styles,
    ]
    return node_setup


def setup_node_styles(_: Style, parent_node: Node = None, node_styles: InheritedDict = None, **__):
    if node_styles is not None:
        return
    if '_node_styles' not in parent_node.node_globals:
        parent_node.node_globals['_node_styles'] = InheritedDict()
    return {'node_styles': parent_node.node_globals['_node_styles']}


def apply_style_items(node: Style, **_):
    """Parsing step. Parses attributes to style items and sets them to style"""
    attrs = node.xml_node.attrs
    try:
        node.name = next(attr.value for attr in attrs if attr.name == 'name')
    except StopIteration:
        raise StyleError('Style name is missing', node.xml_node.view_info)
    node.items = {attr.name: _get_style_item(node, attr) for attr in attrs if attr.name != 'name'}


def _get_style_item(node: Style, attr: XmlAttr):
    setter = get_setter(attr)
    value = attr.value if attr.value else ''
    if is_expression(value):
        expression_ = expression(parse_expression(value)[1])
        value = expression_.execute(node.node_globals.to_dictionary())
    return StyleItem(setter, attr.name, value)


def apply_parent_items(node: Style, parent_node: Style = None, **_):
    """Sets style items from parent style"""
    if isinstance(parent_node, Style):
        node.items = {**parent_node.items, **node.items}


def store_to_node_styles(node: Style, node_styles: InheritedDict = None, **_):
    """Store styles to node styles"""
    node_styles[node.name] = node.items.values()


def render_child_styles(node: Style, node_styles: InheritedDict = None, **_):
    """Renders child styles"""
    render_children(node,
                    parent_node=node,
                    node_globals=InheritedDict(node.node_globals),
                    node_styles=node_styles)


def get_styles_view_pipeline() -> RenderingPipeline:
    """Returns setup for container"""
    return RenderingPipeline(steps=[
        apply_attributes,
        render_view_children,
        store_to_globals
    ])


def store_to_globals(view: StylesView, parent_node: Node = None, **_):
    child: Node = view.children[0]
    styles: InheritedDict = child.node_globals['_node_styles']
    if '_node_styles' in parent_node.node_globals:
        parent_styles = parent_node.node_globals['_node_styles']
        merged_styles = {**parent_styles.to_dictionary(), **styles.to_dictionary()}
        styles = InheritedDict(merged_styles)
    parent_node.node_globals['_node_styles'] = styles
