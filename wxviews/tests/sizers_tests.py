from unittest.mock import Mock, call, patch

from pytest import fail, mark
from wx import Sizer

from wxviews.core import WxRenderingContext
from wxviews.core.pipeline import instance_node_setter
from wxviews import sizers
from wxviews.sizers import SizerNode, GrowableCol, GrowableRow, sizer
from wxviews.sizers import setup_setter, render_sizer_children, set_sizer_to_parent
from wxviews.sizers import add_growable_row_to_sizer, add_growable_col_to_sizer


class SizerNodeTests:
    """SizerNode tests"""

    @staticmethod
    def test_removes_sizer_from_parent():
        """should remove sizer from parent"""
        parent = Mock()
        node = SizerNode(Mock(), Mock(), parent=parent)

        node.destroy()

        assert parent.SetSizer.call_args == call(None, True)

    @staticmethod
    def test_do_nothing_if_has_parent_sizer():
        """should do nothing if has parent sizer"""
        parent = Mock()
        node = SizerNode(Mock(), Mock(), parent=parent, sizer=Mock())

        node.destroy()

        assert not parent.SetSizer.called


def test_setup_setter():
    """setup_setter should set instance_node_setter"""
    node = Mock()

    setup_setter(node, WxRenderingContext())

    assert node.attr_setter == instance_node_setter  # pylint: disable=comparison-with-callable


@patch(sizers.__name__ + '.render_children')
@patch(sizers.__name__ + '.InheritedDict')
def test_render_sizer_children(inherited_dict: Mock, render_children: Mock):
    """should pass right child args to render_children"""
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

    render_sizer_children(node, WxRenderingContext({'parent': parent}))

    assert render_children.call_args == call(node, WxRenderingContext(expected_args))


class AnySizer(Sizer):
    def __init__(self):
        self.SetSizer = Mock()


class SetSizerToParentTests:
    """set_sizer_to_parent tests"""

    @staticmethod
    def test_calls_parent_set_sizer():
        """should call SetSizer of parent and pass sizer as argument"""
        node = Mock()
        parent = Mock()

        set_sizer_to_parent(node, WxRenderingContext({'parent': parent}))

        assert parent.SetSizer.call_args == call(node.instance, True)

    @staticmethod
    def test_does_not_calls_parent_set_sizer():
        """should not call SetSizer of parent if parent is sizer"""
        node = Mock()
        parent = AnySizer()

        set_sizer_to_parent(node, WxRenderingContext({'parent': parent, 'sizer': Mock()}))

        assert not parent.SetSizer.called

    @staticmethod
    def test_passes_if_parent_none():
        """should pass if parent is None"""
        node = Mock()

        try:
            set_sizer_to_parent(node, WxRenderingContext({'parent': None}))
        except BaseException:
            fail()


@mark.parametrize('properties, expected_call', [
    ({'idx': 1}, call(1, 0)),
    ({'idx': 1, 'proportion': 1}, call(1, 1)),
    ({'proportion': 1}, call(None, 1))
])
def test_add_growable_row_to_sizer(properties: dict, expected_call: call):
    """should call AddGrowableRow with parameters"""
    node = GrowableRow(Mock())
    sizer_ = Mock()
    for key, value in properties.items():
        node.set_attr(key, value)

    add_growable_row_to_sizer(node, WxRenderingContext({'sizer': sizer_}))

    assert sizer_.AddGrowableRow.call_args == expected_call


@mark.parametrize('properties, expected_call', [
    ({'idx': 1}, call(1, 0)),
    ({'idx': 1, 'proportion': 1}, call(1, 1)),
    ({'proportion': 1}, call(None, 1))
])
def test_add_glowable_col(properties: dict, expected_call: call):
    """should call AddGrowableCol with parameters"""
    node = GrowableCol(Mock())
    sizer_ = Mock()
    for key, value in properties.items():
        node.set_attr(key, value)

    add_growable_col_to_sizer(node, WxRenderingContext({'sizer': sizer_}))

    assert sizer_.AddGrowableCol.call_args == expected_call


@mark.parametrize('key, value, expected_args', [
    ('key', 'value', {'key': 'value'}),
    ('', {'key': 'value'}, {'key': 'value'})
])
def test_sizer(key, value, expected_args):
    """sizer should add key value to sizer_args property"""
    node = Mock(sizer_args={})

    sizer(node, key, value)

    assert expected_args == node.sizer_args
