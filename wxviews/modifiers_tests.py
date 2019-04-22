from itertools import chain
from unittest import TestCase
from unittest.mock import Mock, call
import wx
from pyviews.core import InheritedDict
from pyviews.testing import case

from wxviews.node import StyleError
from wxviews.modifiers import bind, sizer, style


class bind_tests(TestCase):
    @case('EVT_MOVE', print)
    @case('EVT_BUTTON', lambda ev: 2 + 2)
    @case('EVT_SHOW', lambda ev: None)
    def test_binds_commands(self, event_key: str, command):
        node = Mock()
        bind(node, event_key, command)

        msg = 'should call bind method of node with event and command'
        self.assertEqual(node.bind.call_args, call(wx.__dict__[event_key], command), msg)

    @case('EVT_MENU', lambda ev: None, {'id': 105})
    @case('EVT_BUTTON', lambda ev: 2 + 2, {'arg': 'a'})
    def test_binds_commands_with_args(self, event_key: str, command, args: dict):
        node = Mock()
        bind(node, event_key, (command, args))

        msg = 'should call bind method of node with event and command'
        self.assertEqual(node.bind.call_args, call(wx.__dict__[event_key], command, **args), msg)

class sizer_tests(TestCase):
    @case('key', 'value', {'key': 'value'})
    @case('', {'key': 'value'}, {'key': 'value'})
    def test_sets_argument(self, key, value, expected_args):
        node = Mock(sizer_args={})

        sizer(node, key, value)

        msg = 'sizer should add key value to sizer_args property'
        self.assertDictEqual(expected_args, node.sizer_args, msg=msg)

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
        node.node_globals['_node_styles'] = InheritedDict(source=node_styles)

        style(node, None, style_keys)
        called = True
        for item in chain(*node_styles.values()):
            called = item.apply.called and called

        msg = 'should apply style items'
        self.assertTrue(called, msg=msg)

    def test_applies_style_items(self):
        node = Mock(node_globals=InheritedDict())
        item = Mock(apply=Mock())
        node.node_globals['_node_styles'] = InheritedDict(source={'key': [item]})

        style(node, None, 'key')

        msg = 'should pass node to StyleItem.apply'
        self.assertEqual(call(node), item.apply.call_args, msg=msg)

    def test_raises_style_error(self):
        node = Mock(node_globals=InheritedDict())
        node.node_globals['_node_styles'] = InheritedDict()

        msg = 'should raise StyleError if style is not found'
        with self.assertRaises(StyleError, msg=msg):
            style(node, None, 'key')
