"""Contains rendering steps for style nodes"""

from typing import Any, List

from injectool import resolve
from pyviews.core import XmlAttr, InheritedDict, Node, CoreError, Modifier, XmlNode, Expression
from pyviews.compilation import is_expression, parse_expression
from pyviews.rendering import get_setter, render_children, RenderingPipeline, apply_attributes
from wxviews.containers import render_view_children
from wxviews.core import WxRenderingContext

STYLES_KEY = '_node_styles'


class StyleError(CoreError):
    """Error for style"""


class StyleItem:
    """Wrapper under option"""

    def __init__(self, modifier: Modifier, name: str, value: Any):
        self._modifier = modifier
        self._name = name
        self._value = value

    @property
    def setter(self):
        """Returns setter"""
        return self._modifier

    @property
    def name(self):
        """Returns name"""
        return self._name

    @property
    def value(self):
        """Returns value"""
        return self._value

    def apply(self, node: Node):
        """Applies option to passed node"""
        self._modifier(node, self._name, self._value)

    def __hash__(self):
        return hash((self._name, self._modifier))

    def __eq__(self, other):
        return hash(self) == hash(other)


class Style(Node):
    """Node for storing config options"""

    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(xml_node, node_globals)
        self.name = None
        self.items = {}


def get_style_pipeline() -> RenderingPipeline:
    """Returns pipeline for style node"""
    return RenderingPipeline(steps=[
        setup_node_styles,
        apply_style_items,
        apply_parent_items,
        store_to_node_styles,
        render_child_styles
    ])


def setup_node_styles(_: Style, context: WxRenderingContext):
    """Initializes node styles"""
    if STYLES_KEY not in context.parent_node.node_globals:
        context.parent_node.node_globals[STYLES_KEY] = InheritedDict()


def _get_styles(context: WxRenderingContext) -> InheritedDict:
    return context.parent_node.node_globals[STYLES_KEY]


def apply_style_items(node: Style, _: WxRenderingContext):
    """Parsing step. Parses attributes to style items and sets them to style"""
    attrs = node.xml_node.attrs
    try:
        node.name = next(attr.value for attr in attrs if attr.name == 'name')
    except StopIteration:
        raise StyleError('Style name is missing', node.xml_node.view_info)
    node.items = {
        f'{attr.namespace}{attr.name}':
            _get_style_item(node, attr) for attr in attrs if attr.name != 'name'
    }


def _get_style_item(node: Style, attr: XmlAttr):
    setter = get_setter(attr)
    value = attr.value if attr.value else ''
    if is_expression(value):
        expression_ = resolve(Expression, parse_expression(value)[1])
        value = expression_.execute(node.node_globals.to_dictionary())
    return StyleItem(setter, attr.name, value)


def apply_parent_items(node: Style, context: WxRenderingContext):
    """Sets style items from parent style"""
    if isinstance(context.parent_node, Style):
        node.items = {**context.parent_node.items, **node.items}


def store_to_node_styles(node: Style, context: WxRenderingContext):
    """Store styles to node styles"""
    _get_styles(context)[node.name] = node.items.values()


def render_child_styles(node: Style, context: WxRenderingContext):
    """Renders child styles"""
    render_children(node, WxRenderingContext({
        'parent_node': node,
        'node_globals': InheritedDict(node.node_globals),
        'node_styles': _get_styles(context)
    }))


class StylesView(Node):
    """Loads styles from separate file"""

    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(xml_node, node_globals)
        self.name = None


def get_styles_view_pipeline() -> RenderingPipeline:
    """Returns setup for container"""
    return RenderingPipeline(steps=[
        apply_attributes,
        render_view_children,
        store_to_globals
    ])


def store_to_globals(view: StylesView, context: WxRenderingContext):
    """Stores styles to parent node globals"""
    child: Node = view.children[0]
    styles: InheritedDict = child.node_globals[STYLES_KEY]
    if STYLES_KEY in context.parent_node.node_globals:
        parent_styles = context.parent_node.node_globals[STYLES_KEY]
        merged_styles = {**parent_styles.to_dictionary(), **styles.to_dictionary()}
        styles = InheritedDict(merged_styles)
    context.parent_node.node_globals[STYLES_KEY] = styles


def style(node: Node, _: str, keys: List[str]):
    """Applies styles to node"""
    if isinstance(keys, str):
        keys = [key.strip() for key in keys.split(',') if key]
    try:
        node_styles = node.node_globals[STYLES_KEY]
        for key in keys:
            for item in node_styles[key]:
                item.apply(node)
    except KeyError as key_error:
        error = StyleError('Style is not found')
        error.add_info('Style name', key_error.args[0])
        raise error from key_error
