from typing import cast
from unittest.mock import Mock, call, patch

from pytest import mark, raises
from pyviews.core import XmlNode
from wx import EVT_MENU, EVT_BUTTON

from wxviews import widgets
from wxviews.core import WxRenderingContext
from wxviews.widgets import render_wx_children, WidgetNode, store_root, get_root


class WidgetNodeTests:
    """WidgetNode tests"""

    @staticmethod
    def test_destroys_instance():
        """should destroy instance"""
        instance = Mock()
        node = WidgetNode(instance, XmlNode('', ''))

        node.destroy()

        assert instance.Destroy.called

    @staticmethod
    @mark.parametrize('event, callback, args', [
        (EVT_MENU, lambda evt: None, {}),
        (EVT_MENU, lambda evt: None, {'id': 105}),
        (EVT_BUTTON, lambda evt: print('button'), {})
    ])
    def test_calls_instance_bind(event, callback, args: dict):
        """should call bind for instance"""
        instance = Mock()
        instance.bind = Mock()
        node = WidgetNode(instance, XmlNode('', ''))

        node.bind(event, callback, **args)

        assert node.instance.Bind.call_args == call(event, callback, **args)


@patch(widgets.__name__ + '.render_children')
@patch(widgets.__name__ + '.InheritedDict')
def test_render_wx_children(inherited_dict: Mock, render_children: Mock):
    """should pass right child args to render_children"""
    node = Mock(instance=Mock(), node_globals=Mock())
    sizer = Mock()
    child_globals = Mock()
    inherited_dict.side_effect = lambda a: child_globals
    expected_args = {
        'parent': node.instance,
        'parent_node': node,
        'node_globals': child_globals
    }

    render_wx_children(node, WxRenderingContext({'sizer': sizer}))

    assert render_children.call_args == call(node, WxRenderingContext(expected_args))


def test_root():
    """store_root should set WidgetNode.Root to passed node"""
    node = Mock()

    store_root(node, WxRenderingContext())

    assert get_root() == node


def test_get_root():
    store_root(cast(WidgetNode, None), WxRenderingContext())

    with raises(ValueError):
        get_root()
