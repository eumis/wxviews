'''WxNode tests'''

# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock
from wxviews.core.node import WxNode

class WxNode_init_tests(TestCase):
    def test_sets_instance(self):
        node = WxNode(None)
        instance = Mock()

        node.init(instance)

        msg = 'should destroy instance'
        self.assertEqual(node.instance, instance, msg)

class WxNode_destroy_tests(TestCase):
    def test_destroys_instance(self):
        node = WxNode(None)
        instance = Mock()
        node.init(instance)

        node.destroy()

        msg = 'should destroy instance'
        self.assertTrue(instance.Destroy.called, msg)

if __name__ == '__main__':
    main()
