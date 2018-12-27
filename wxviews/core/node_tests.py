'''WxNode tests'''

# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call
from wx import EVT_MENU, EVT_BUTTON
from pyviews.testing import case
from wxviews.core.node import WxNode

class WxNode_destroy_tests(TestCase):
    def test_destroys_instance(self):
        instance = Mock()
        node = WxNode(instance, None)

        node.destroy()

        msg = 'should destroy instance'
        self.assertTrue(instance.Destroy.called, msg)

class WxNode_bind_tests(TestCase):
    @case(EVT_MENU, lambda evt: None, {})
    @case(EVT_MENU, lambda evt: None, {'id':105})
    @case(EVT_BUTTON, lambda evt: print('button'), {})
    def test_calls_instance_bind(self, event, callback, args: dict):
        instance = Mock()
        instance.bind = Mock()
        node = WxNode(instance, None)

        node.bind(event, callback, **args)

        msg = 'should call bind for instance'
        self.assertEqual(node.instance.Bind.call_args, call(event, callback, **args), msg)

if __name__ == '__main__':
    main()
