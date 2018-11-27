'''WxNode rendering pipeline tests'''

# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call, patch
from wx import Sizer # pylint: disable=E0611
from wxviews.pipeline.common import instance_node_setter
from wxviews.pipeline.sizers import setup_setter, render_sizer_children, set_sizer_to_parent

class setup_setter_tests(TestCase):
    def test_sets_instance_property(self):
        node = Mock()
        setup_setter(node)

        msg = 'setup_setter should set instance_node_setter'
        self.assertEqual(node.attr_setter, instance_node_setter, msg)

class render_sizer_children_tests(TestCase):
    @patch('wxviews.pipeline.sizers.render_children')
    @patch('wxviews.pipeline.sizers.InheritedDict')
    def test_passes_child_args(self, inherited_dict: Mock, render_children: Mock):
        node = Mock(instance=Mock(), node_globals=Mock())
        parent = Mock()
        child_globals = Mock()
        inherited_dict.side_effect = lambda a: child_globals
        expected_args = {
            'parent_node': node,
            'parent': parent,
            'node_globals': child_globals,
            'sizer': node.instance
        }

        render_sizer_children(node, parent=parent)

        msg = 'should pass right child args to render_children'
        self.assertEqual(render_children.call_args, call(node, **expected_args), msg)

class AnySizer(Sizer):
    def __init__(self):
        self.SetSizer = Mock()

class set_sizer_to_parent_tests(TestCase):
    def test_calls_parent_SetSizer(self):
        node = Mock()
        parent = Mock()

        set_sizer_to_parent(node, parent=parent)

        msg = 'should call SetSizer of parent and pass sizer as argument'
        self.assertEqual(parent.SetSizer.call_args, call(node.instance), msg)

    def test_not_calls_SetSizer_if_parent_sizer(self):
        node = Mock()
        parent = AnySizer()

        set_sizer_to_parent(node, parent=parent, sizer=Mock())

        msg = 'should not call SetSizer of parent if parent is sizer'
        self.assertFalse(parent.SetSizer.called, msg)

    def test_passes_if_parent_none(self):
        node = Mock()

        try:
            set_sizer_to_parent(node, parent=None)
        except:
            self.fail('should pass if parent is None')

if __name__ == '__main__':
    main()
