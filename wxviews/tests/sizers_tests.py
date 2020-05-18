from unittest.mock import Mock, call, patch

from injectool import add_singleton
from pytest import fail, mark
from pyviews.rendering import render
from wx import Sizer

from wxviews import sizers
from wxviews.core import WxRenderingContext
from wxviews.sizers import SizerNode, GrowableCol, GrowableRow, set_sizer
from wxviews.sizers import add_growable_row_to_sizer, add_growable_col_to_sizer
from wxviews.sizers import render_sizer_children, set_sizer_to_parent


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


@mark.usefixtures('container_fixture')
@mark.parametrize('nodes_count', [1, 2, 5])
def test_render_sizer_children(nodes_count):
    """should render all xml children for every item"""
    render_mock = Mock()
    add_singleton(render, render_mock)
    with patch(sizers.__name__ + '.InheritedDict') as inherited_dict_mock:
        inherited_dict_mock.side_effect = lambda p: {'source': p} if p else p
        xml_node = Mock(children=[Mock() for _ in range(nodes_count)])
        parent, node = Mock(), SizerNode(Mock(), xml_node)
        context = WxRenderingContext({'node': node, 'parent': parent})

        render_sizer_children(node, context)

        for actual_call, child_xml_node in zip(render_mock.call_args_list, xml_node.children):
            child_context = WxRenderingContext({
                'parent_node': node,
                'parent': parent,
                'node_globals': inherited_dict_mock(node.node_globals),
                'sizer': node.instance,
                'xml_node': child_xml_node
            })
            assert actual_call == call(child_context)


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

    set_sizer(node, key, value)

    assert expected_args == node.sizer_args
