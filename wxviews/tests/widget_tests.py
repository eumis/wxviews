from unittest import TestCase
from unittest.mock import Mock, call, patch

from pyviews.testing import case
from wx import EVT_MENU, EVT_BUTTON

from wxviews import widgets
from wxviews.widgets import render_wx_children, WidgetNode


class WidgetNode_destroy_tests(TestCase):
    def test_destroys_instance(self):
        instance = Mock()
        node = WidgetNode(instance, None)

        node.destroy()

        msg = 'should destroy instance'
        self.assertTrue(instance.Destroy.called, msg)


class WidgetNode_bind_tests(TestCase):
    @case(EVT_MENU, lambda evt: None, {})
    @case(EVT_MENU, lambda evt: None, {'id': 105})
    @case(EVT_BUTTON, lambda evt: print('button'), {})
    def test_calls_instance_bind(self, event, callback, args: dict):
        instance = Mock()
        instance.bind = Mock()
        node = WidgetNode(instance, None)

        node.bind(event, callback, **args)

        msg = 'should call bind for instance'
        self.assertEqual(node.instance.Bind.call_args, call(event, callback, **args), msg)


class render_wx_children_tests(TestCase):
    @patch(widgets.__name__ + '.render_children')
    @patch(widgets.__name__ + '.InheritedDict')
    def test_passes_child_args(self, inherited_dict: Mock, render_children: Mock):
        node = Mock(instance=Mock(), node_globals=Mock())
        sizer = Mock()
        child_globals = Mock()
        inherited_dict.side_effect = lambda a: child_globals
        expected_args = {
            'parent': node.instance,
            'parent_node': node,
            'node_globals': child_globals
        }

        render_wx_children(node, sizer=sizer)

        msg = 'should pass right child args to render_children'
        self.assertEqual(render_children.call_args, call(node, **expected_args), msg)
