from unittest import TestCase, main
from unittest.mock import Mock, call
import wx
from wx.lib.newevent import NewEvent
from pyviews.core.ioc import Scope, register_single, scope
from pyviews.testing import case
from wxviews.modifiers import call as call_mod, setup_sizer, bind

class ModifiersTest(TestCase):
    def setUp(self):
        with Scope('ModifierTest'):
            register_single('custom_events', {})

    @case('method', 'one', call('one'))
    @case('method', 1, call(1))
    @case('method', ['one'], call('one'))
    @case('method', [[1]], call([1]))
    @case('method', ['one', 2], call('one', 2))
    @case('method', ('one', 2), call('one', 2))
    def test_call(self, key, args, call_args):
        node = Mock()
        call_mod(node, key, args)

        msg = 'call should call method by key'
        self.assertTrue(getattr(node.instance, key).called, msg)

        msg = 'call should pass arguments to method'
        self.assertEqual(getattr(node.instance, key).call_args, call_args, msg)

    @case([])
    @case([1, 2])
    @case(['value', 2])
    def test_setup_sizer_args(self, value):
        node = Mock()
        node.sizer_args = []
        setup_sizer(node, 'args', value)

        msg = 'setup_sizer should set sizer_args property if "args" key passed'
        self.assertEqual(node.sizer_args, value, msg)

    @case({'key': 'value'})
    @case({'key': 'value', 'another key': 2})
    @case({})
    def test_setup_sizer_kwargs(self, kwargs):
        node = Mock()
        node.sizer_kwargs = {}
        setup_sizer(node, 'kwargs', kwargs)

        msg = 'setup_sizer should set sizer_kwargs property if "kwargs" key passed'
        self.assertEqual(node.sizer_kwargs, kwargs, msg)

    @scope('ModifierTest')
    @case('EVT_MENU', lambda ev: None)
    @case('EVT_MOVE', lambda ev: None)
    @case('EVT_BUTTON', lambda ev: None)
    def test_bind(self, event_key, command):
        node = Mock()
        bind(node, event_key, command)

        msg = 'bind should pass event from wx namespace by key and command'
        self.assertEqual(node.bind.call_args, call(wx.__dict__[event_key], command), msg)

    @scope('ModifierTest')
    @case('EVT_CUSTOM', lambda ev: None)
    @case('custom', lambda ev: None)
    def test_bind_custom_event(self, event_key, command):
        custom_event = NewEvent()[1]
        register_single('custom_events', {event_key: custom_event})

        node = Mock()
        bind(node, event_key, command)

        msg = 'bind should pass custom event by key and command'
        self.assertEqual(node.bind.call_args, call(custom_event, command), msg)

    @scope('ModifierTest')
    @case('some_Event')
    @case('EVT_BUTTONN')
    def test_bind_raises(self, event_key):
        with self.assertRaises(KeyError):
            bind(Mock(), event_key, lambda ev: None)

if __name__ == '__main__':
    main()
