from unittest import TestCase
from unittest.mock import Mock, call, patch
from wx import Sizer
from pyviews.testing import case
from wxviews.core.pipeline import instance_node_setter
from wxviews import sizers
from wxviews.sizers import SizerNode, GrowableCol, GrowableRow, sizer
from wxviews.sizers import setup_setter, render_sizer_children, set_sizer_to_parent
from wxviews.sizers import add_growable_row_to_sizer, add_growable_col_to_sizer


class SizerNode_destroy_test(TestCase):
    def test_removes_sizer_from_parent(self):
        parent = Mock()
        node = SizerNode(Mock(), Mock(), parent=parent)

        node.destroy()

        msg = 'should remove sizer from parent'
        self.assertEqual(parent.SetSizer.call_args, call(None, True), msg)

    def test_do_nothing_if_has_parent_sizer(self):
        parent = Mock()
        node = SizerNode(Mock(), Mock(), parent=parent, sizer=Mock())

        node.destroy()

        msg = 'should do nothing if has parent sizer'
        self.assertFalse(parent.SetSizer.called, msg)


class setup_setter_tests(TestCase):
    def test_sets_instance_property(self):
        node = Mock()
        setup_setter(node)

        msg = 'setup_setter should set instance_node_setter'
        self.assertEqual(node.attr_setter, instance_node_setter, msg)


class render_sizer_children_tests(TestCase):
    @patch(sizers.__name__ + '.render_children')
    @patch(sizers.__name__ + '.InheritedDict')
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
        self.assertEqual(parent.SetSizer.call_args, call(node.instance, True), msg)

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


class add_growable_row_to_sizer_tests(TestCase):
    @case({'idx': 1}, call(1, 0))
    @case({'idx': 1, 'proportion': 1}, call(1, 1))
    @case({'proportion': 1}, call(None, 1))
    def test_calls_AddGrowableRow(self, properties: dict, expected_call: call):
        node = GrowableRow(Mock())
        sizer = Mock()
        for key, value in properties.items():
            node.set_attr(key, value)

        add_growable_row_to_sizer(node, sizer=sizer)

        msg = 'should call AddGrowableRow with parameters'
        self.assertEqual(sizer.AddGrowableRow.call_args, expected_call, msg)


class add_growable_col_to_sizer_tests(TestCase):
    @case({'idx': 1}, call(1, 0))
    @case({'idx': 1, 'proportion': 1}, call(1, 1))
    @case({'proportion': 1}, call(None, 1))
    def test_calls_AddGrowableCol(self, properties: dict, expected_call: call):
        node = GrowableCol(Mock())
        sizer = Mock()
        for key, value in properties.items():
            node.set_attr(key, value)

        add_growable_col_to_sizer(node, sizer=sizer)

        msg = 'should call AddGrowableCol with parameters'
        self.assertEqual(sizer.AddGrowableCol.call_args, expected_call, msg)


class sizer_tests(TestCase):
    @case('key', 'value', {'key': 'value'})
    @case('', {'key': 'value'}, {'key': 'value'})
    def test_sets_argument(self, key, value, expected_args):
        node = Mock(sizer_args={})

        sizer(node, key, value)

        msg = 'sizer should add key value to sizer_args property'
        self.assertDictEqual(expected_args, node.sizer_args, msg=msg)
