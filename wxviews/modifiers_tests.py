# pylint: disable=C0111,C0103

from unittest import TestCase
from unittest.mock import Mock, call
import wx
from pyviews.testing import case
from wxviews.modifiers import bind, sizer 

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
