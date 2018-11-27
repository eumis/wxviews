'''WxNode rendering pipeline tests'''

# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call, patch
from wxviews.pipeline.common import instance_node_setter
from wxviews.pipeline.instance import setup_setter, render_wx_children

class setup_setter_tests(TestCase):
    def test_sets_instance_property(self):
        node = Mock()
        setup_setter(node)

        msg = 'setup_setter should set instance_node_setter'
        self.assertEqual(node.attr_setter, instance_node_setter, msg)

class render_wx_children_tests(TestCase):
    @patch('wxviews.pipeline.instance.render_children')
    @patch('wxviews.pipeline.instance.InheritedDict')
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

if __name__ == '__main__':
    main()
