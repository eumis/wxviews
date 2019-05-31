from itertools import chain
from unittest.mock import Mock

from injectool import Scope, register_func
from pytest import mark, raises
from pyviews.core import XmlAttr, InheritedDict, Node, Expression
from pyviews.compilation import CompiledExpression
from pyviews.rendering import call_set_attr
from wxviews.styles import Style, StyleError, StylesView, style, STYLES_KEY
from wxviews.styles import setup_node_styles, apply_style_items, apply_parent_items, store_to_globals
from wxviews.styles import store_to_node_styles

with Scope('styles_tests'):
    register_func(Expression, CompiledExpression)


def some_setter():
    """Some test setter"""


def another_setter():
    """Another test setter"""


class SetupNodeStylesTest:
    """setup_node_styles tests"""

    @staticmethod
    def test_creates_node_styles():
        """should add node_styles to parent globals"""
        parent_node: Node = Mock(node_globals=InheritedDict())

        setup_node_styles(Mock(), parent_node=parent_node, node_styles=None)
        actual = parent_node.node_globals.get(STYLES_KEY)

        assert isinstance(actual, InheritedDict)

    @staticmethod
    def test_does_not_create_if_exist():
        """should not change parent node_globals if node_styles exist"""
        node_styles = InheritedDict()
        parent_node: Node = Mock(node_globals=InheritedDict({STYLES_KEY: node_styles}))

        setup_node_styles(Mock(), parent_node=parent_node, node_styles=None)
        actual = parent_node.node_globals[STYLES_KEY]

        assert node_styles == actual

    @staticmethod
    def test_returns_node_styles():
        """should return created node_styles"""
        parent_node: Node = Mock(node_globals=InheritedDict())

        result = setup_node_styles(Mock(), parent_node=parent_node, node_styles=None)
        actual = result['node_styles']
        expected = parent_node.node_globals.get(STYLES_KEY)

        assert expected == actual

    @staticmethod
    def test_returns_none_if_exist():
        """should return created node_styles"""
        actual = setup_node_styles(Mock(), node_styles=InheritedDict())

        assert actual is None


class ApplyStyleItemsTests:
    """apply_style_items tests"""

    @staticmethod
    @mark.parametrize('attrs, expected', [
        ([('one', '{1}', None)], [('one', 1, call_set_attr)]),
        ([('one', ' value ', None)], [('one', ' value ', call_set_attr)]),
        ([('one', 'value', __name__ + '.some_setter')], [('one', 'value', some_setter)]),
        (
                [
                    ('one', 'value', __name__ + '.some_setter'),
                    ('two', '{1 + 1}', None),
                    ('key', '', __name__ + '.another_setter')
                ],
                [
                    ('one', 'value', some_setter),
                    ('two', 2, call_set_attr),
                    ('key', '', another_setter)
                ]
        )
    ])
    def test_creates_style_items_from_attrs(attrs, expected):
        """apply_style_items should create style item for every attribute"""
        attrs = [XmlAttr('name', 'hoho')] + [XmlAttr(attr[0], attr[1], attr[2]) for attr in attrs]
        xml_node = Mock(attrs=attrs)
        node = Style(xml_node)

        with Scope('styles_tests'):
            apply_style_items(node)
        actual = {name: (item.name, item.value, item.setter) for name, item in node.items.items()}
        expected = {item[0]: item for item in expected}

        assert actual == expected

    @staticmethod
    def test_requires_name_attribute():
        """apply_style_items should raise StyleError if name attribute is missing"""
        xml_node = Mock(attrs=[])
        node = Style(xml_node)

        with raises(StyleError):
            apply_style_items(node)

    @staticmethod
    @mark.parametrize('name', [
        '',
        'name',
        'some name',
        ' some name    ',
    ])
    def test_sets_style_name(name):
        """apply_style_items should set style name from attributes"""
        xml_node = Mock(attrs=[XmlAttr('name', name)])
        node = Style(xml_node)

        with Scope('styles_tests'):
            apply_style_items(node)

        assert node.name == name


class ApplyParentItemsTests:
    """apply_parent_items tests"""

    @staticmethod
    @mark.parametrize('items, parent_items, expected', [
        (
                [('one', 'value'), ('key', '')],
                [('one', 'parent value'), ('two', 2)],
                [('one', 'value'), ('key', ''), ('two', 2)]
        ),
        (
                [],
                [('one', 'value'), ('two', 2)],
                [('one', 'value'), ('two', 2)]
        ),
        (
                [('one', 'value'), ('two', 2)],
                [],
                [('one', 'value'), ('two', 2)]
        ),
    ])
    def test_uses_parent_style_items(items, parent_items, expected):
        """apply_parent_items should add parent style items"""
        node = Style(Mock())
        node.items = {item[0]: item for item in items}
        parent_node = Style(Mock())
        parent_node.items = {item[0]: item for item in parent_items}
        expected = {item[0]: item for item in expected}

        apply_parent_items(node, parent_node=parent_node)

        assert node.items == expected

    @staticmethod
    @mark.parametrize('parent_node', [None, Node(Mock())])
    def test_skips_not_style_parent(parent_node):
        """apply_parent_items do nothing if parent is not Style"""
        items = {'item': ('item', 'value')}
        node = Style(Mock())
        node.items = items.copy()

        apply_parent_items(node, parent_node=parent_node)

        assert items == node.items


def test_store_to_node_styles():
    """store_to_node_styles should store style items to node_styles"""
    node_styles = InheritedDict()
    node = Style(Mock())
    node.items = Mock()

    store_to_node_styles(node, node_styles=node_styles)

    assert node_styles[node.name] == node.items.values()


@mark.parametrize('parent_styles, view_styles, expected', [
    (None, {}, {}),
    ({}, {}, {}),
    (None, {'key': 'style'}, {'key': 'style'}),
    ({}, {'key': 'style'}, {'key': 'style'}),
    ({'key': 'style'}, {'style': 'style'}, {'key': 'style', 'style': 'style'}),
    ({'key': 'parent style'}, {'key': 'view style'}, {'key': 'view style'})
])
def test_store_to_globals(parent_styles, view_styles, expected):
    """should copy node styles from view root to parent globals"""
    parent_node = Mock(node_globals=InheritedDict())
    if parent_styles:
        parent_node.node_globals[STYLES_KEY] = InheritedDict(parent_styles)
    node = StylesView(Mock())
    child = Mock(node_globals=InheritedDict())
    child.node_globals[STYLES_KEY] = InheritedDict(view_styles)
    node.add_child(child)

    store_to_globals(node, parent_node=parent_node)
    actual = parent_node.node_globals[STYLES_KEY].to_dictionary()

    assert expected == actual


class StyleTests:
    """style tests"""

    @staticmethod
    @mark.parametrize('style_keys, expected_keys', [
        ('one, two', ['one', 'two']),
        ('two, one', ['one', 'two']),
        ('one', ['one']),
        ('', []),
        (['one', 'two'], ['one', 'two']),
        (['two', 'one'], ['one', 'two']),
        (['one'], ['one']),
        ([''], ['']),
        ([], []),
    ])
    def test_applies_style_items(style_keys, expected_keys):
        """should apply style items"""
        node = Mock(node_globals=InheritedDict())
        node_styles = {key: [Mock(apply=Mock())] for key in expected_keys}
        node.node_globals[STYLES_KEY] = InheritedDict(source=node_styles)

        style(node, '', style_keys)
        called = True
        for item in chain(*node_styles.values()):
            called = item.apply.called and called

        assert called

    @staticmethod
    def test_raises_style_error():
        """should raise StyleError if style is not found"""
        node = Mock(node_globals=InheritedDict())
        node.node_globals[STYLES_KEY] = InheritedDict()

        with raises(StyleError):
            style(node, '', ['key'])