from unittest import TestCase
from unittest.mock import Mock
from pyviews.testing import case
from pyviews.core import XmlAttr, InheritedDict, Node
from pyviews.core.ioc import Scope, register_func
from pyviews.compilation import CompiledExpression
from pyviews.rendering import call_set_attr
from wxviews.node import Style, StyleError
from .styles import setup_node_styles, apply_style_items, apply_parent_items
from .styles import store_to_node_styles

with Scope('styles_tests'):
    register_func('expression', CompiledExpression)


def some_setter():
    """Some test setter"""


def another_setter():
    """Another test setter"""


class setup_node_styles_test(TestCase):
    def test_creates_node_styles(self):
        parent: Node = Mock(node_globals={})

        setup_node_styles(Mock(), parent=parent, node_styles=None)
        actual = parent.node_globals.get('_node_styles')

        msg = 'should add node_styles to parent globals'
        self.assertIsInstance(actual, InheritedDict, msg=msg)

    def test_does_not_create_if_exist(self):
        parent: Node = Mock(node_globals={})

        setup_node_styles(Mock(), parent=parent, node_styles=None)

        msg = 'should not change parent node_globals if node_styles exist'
        self.assertFalse('_node_styles' not in parent.node_globals, msg=msg)

    def test_returns_node_styles(self):
        parent: Node = Mock(node_globals={})

        actual = setup_node_styles(Mock(), parent=parent, node_styles=None)
        expected = parent.node_globals.get('_node_styles')

        msg = 'should return created node_styles'
        self.assertEqual(expected, actual, msg=msg)

    def test_returns_none_if_exist(self):
        actual = setup_node_styles(Mock(), node_styles=InheritedDict())

        msg = 'should return created node_styles'
        self.assertIsNone(actual, msg=msg)


class apply_style_items_tests(TestCase):
    @case([('one', '{1}', None)], [('one', 1, call_set_attr)])
    @case([('one', ' value ', None)], [('one', ' value ', call_set_attr)])
    @case([('one', 'value', __name__ + '.some_setter')], [('one', 'value', some_setter)])
    @case(
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
    def test_creates_style_items_from_attrs(self, attrs, expected):
        attrs = [XmlAttr('name', 'hoho')] + [XmlAttr(attr[0], attr[1], attr[2]) for attr in attrs]
        xml_node = Mock(attrs=attrs)
        node = Style(xml_node)

        with Scope('styles_tests'):
            apply_style_items(node)
        actual = {name: (item.name, item.value, item.setter) for name, item in node.items.items()}
        expected = {item[0]: item for item in expected}

        msg = 'apply_style_items should create style item for every attribute'
        self.assertDictEqual(actual, expected, msg)

    def test_requires_name_attribute(self):
        xml_node = Mock(attrs=[])
        node = Style(xml_node)

        msg = 'apply_style_items should raise StyleError if name attribute is missing'
        with self.assertRaises(StyleError, msg=msg):
            apply_style_items(node)

    @case('')
    @case('name')
    @case('some name')
    @case(' some name    ')
    def test_sets_style_name(self, name):
        xml_node = Mock(attrs=[XmlAttr('name', name)])
        node = Style(xml_node)

        with Scope('styles_tests'):
            apply_style_items(node)

        msg = 'apply_style_items should set style name from attributes'
        self.assertEqual(node.name, name, msg)


class apply_parent_items_tests(TestCase):
    @case(
        [('one', 'value'), ('key', '')],
        [('one', 'parent value'), ('two', 2)],
        [('one', 'value'), ('key', ''), ('two', 2)]
    )
    @case(
        [],
        [('one', 'value'), ('two', 2)],
        [('one', 'value'), ('two', 2)]
    )
    @case(
        [('one', 'value'), ('two', 2)],
        [],
        [('one', 'value'), ('two', 2)]
    )
    def test_uses_parent_style_items(self, items, parent_items, expected):
        node = Style(Mock())
        node.items = {item[0]: item for item in items}
        parent = Style(Mock())
        parent.items = {item[0]: item for item in parent_items}
        expected = {item[0]: item for item in expected}

        apply_parent_items(node, parent=parent)

        msg = 'apply_parent_items should add parent style items'
        self.assertDictEqual(node.items, expected, msg)

    @case(None)
    @case(Node(Mock()))
    def test_skips_not_style_parent(self, parent):
        items = {'item': ('item', 'value')}
        node = Style(Mock())
        node.items = items.copy()

        apply_parent_items(node, parent=parent)

        msg = 'apply_parent_items do nothing if parent is not Style'
        self.assertDictEqual(items, node.items, msg)


class store_to_node_styles_tests(TestCase):
    def test_adds_items_to_node_styles(self):
        node_styles = InheritedDict()
        node = Style(Mock())
        node.items = Mock()

        store_to_node_styles(node, node_styles=node_styles)

        msg = 'store_to_node_styles should store style items to node_styles'
        self.assertEqual(node_styles[node.name], node.items.values(), msg)
