from itertools import chain
from unittest import TestCase
from unittest.mock import Mock, call
from pyviews.testing import case
from pyviews.core import XmlAttr, InheritedDict, Node
from pyviews.core.ioc import Scope, register_func
from pyviews.compilation import CompiledExpression
from pyviews.rendering import call_set_attr
from wxviews.styles import Style, StyleError, StylesView, style, STYLES_KEY
from wxviews.styles import setup_node_styles, apply_style_items, apply_parent_items, store_to_globals
from wxviews.styles import store_to_node_styles

with Scope('styles_tests'):
    register_func('expression', CompiledExpression)


def some_setter():
    """Some test setter"""


def another_setter():
    """Another test setter"""


class setup_node_styles_test(TestCase):
    def test_creates_node_styles(self):
        parent_node: Node = Mock(node_globals=InheritedDict())

        setup_node_styles(Mock(), parent_node=parent_node, node_styles=None)
        actual = parent_node.node_globals.get(STYLES_KEY)

        msg = 'should add node_styles to parent globals'
        self.assertIsInstance(actual, InheritedDict, msg=msg)

    def test_does_not_create_if_exist(self):
        node_styles = InheritedDict()
        parent_node: Node = Mock(node_globals=InheritedDict({STYLES_KEY: node_styles}))

        setup_node_styles(Mock(), parent_node=parent_node, node_styles=None)
        actual = parent_node.node_globals[STYLES_KEY]

        msg = 'should not change parent node_globals if node_styles exist'
        self.assertEqual(node_styles, actual, msg=msg)

    def test_returns_node_styles(self):
        parent_node: Node = Mock(node_globals=InheritedDict())

        result = setup_node_styles(Mock(), parent_node=parent_node, node_styles=None)
        actual = result['node_styles']
        expected = parent_node.node_globals.get(STYLES_KEY)

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
        parent_node = Style(Mock())
        parent_node.items = {item[0]: item for item in parent_items}
        expected = {item[0]: item for item in expected}

        apply_parent_items(node, parent_node=parent_node)

        msg = 'apply_parent_items should add parent style items'
        self.assertDictEqual(node.items, expected, msg)

    @case(None)
    @case(Node(Mock()))
    def test_skips_not_style_parent(self, parent_node):
        items = {'item': ('item', 'value')}
        node = Style(Mock())
        node.items = items.copy()

        apply_parent_items(node, parent_node=parent_node)

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


class store_to_globals_tests(TestCase):
    @case(None, {}, {})
    @case({}, {}, {})
    @case(None, {'key': 'style'}, {'key': 'style'})
    @case({}, {'key': 'style'}, {'key': 'style'})
    @case({'key': 'style'}, {'style': 'style'}, {'key': 'style', 'style': 'style'})
    @case({'key': 'parent style'}, {'key': 'view style'}, {'key': 'view style'})
    def test_copies_node_styles(self, parent_styles, view_styles, expected):
        parent_node = Mock(node_globals=InheritedDict())
        if parent_styles:
            parent_node.node_globals[STYLES_KEY] = InheritedDict(parent_styles)
        node = StylesView(Mock())
        child = Mock(node_globals=InheritedDict())
        child.node_globals[STYLES_KEY] = InheritedDict(view_styles)
        node.add_child(child)

        store_to_globals(node, parent_node=parent_node)
        actual = parent_node.node_globals[STYLES_KEY].to_dictionary()

        msg = 'should copy node styles from view root to parent globals'
        self.assertEqual(expected, actual, msg=msg)


class style_tests(TestCase):
    @case('one, two', ['one', 'two'])
    @case('two, one', ['one', 'two'])
    @case('one', ['one'])
    @case('', [])
    @case(['one', 'two'], ['one', 'two'])
    @case(['two', 'one'], ['one', 'two'])
    @case(['one'], ['one'])
    @case([''], [])
    def test_applies_style_items(self, style_keys, expected_keys):
        node = Mock(node_globals=InheritedDict())
        node_styles = {key: [Mock(apply=Mock())] for key in expected_keys}
        node.node_globals[STYLES_KEY] = InheritedDict(source=node_styles)

        style(node, None, style_keys)
        called = True
        for item in chain(*node_styles.values()):
            called = item.apply.called and called

        msg = 'should apply style items'
        self.assertTrue(called, msg=msg)

    def test_applies_style_items(self):
        node = Mock(node_globals=InheritedDict())
        item = Mock(apply=Mock())
        node.node_globals[STYLES_KEY] = InheritedDict(source={'key': [item]})

        style(node, None, 'key')

        msg = 'should pass node to StyleItem.apply'
        self.assertEqual(call(node), item.apply.call_args, msg=msg)

    def test_raises_style_error(self):
        node = Mock(node_globals=InheritedDict())
        node.node_globals[STYLES_KEY] = InheritedDict()

        msg = 'should raise StyleError if style is not found'
        with self.assertRaises(StyleError, msg=msg):
            style(node, None, 'key')
