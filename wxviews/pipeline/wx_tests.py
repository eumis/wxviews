# pylint: disable=C0111,C0103

from unittest import TestCase
from unittest.mock import Mock, call, patch
from . import wx
from .wx import render_wx_children

class render_wx_children_tests(TestCase):
    @patch(wx.__name__ + '.render_children')
    @patch(wx.__name__ + '.InheritedDict')
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
