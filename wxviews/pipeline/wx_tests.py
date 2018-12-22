'''WxNode rendering pipeline tests'''

# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call, patch
from wxviews.pipeline.wx import render_wx_children

class render_wx_children_tests(TestCase):
    @patch('wxviews.pipeline.wx.render_children')
    @patch('wxviews.pipeline.wx.InheritedDict')
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
