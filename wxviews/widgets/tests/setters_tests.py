from unittest.mock import Mock, call

import wx
from pytest import fixture, mark
from pyviews.core.rendering import NodeGlobals
from wx.lib.newevent import NewEvent

from wxviews.widgets import setters
from wxviews.widgets.rendering import WxNode

CustomEvent, EVT_CUSTOM_EVENT = NewEvent()


class BindTests:
    """setters.show() tests"""

    @staticmethod
    @mark.parametrize('event_key, command, args', [
        ('EVT_MOVE', print, None),
        ('EVT_MENU', lambda _: None, {'id': 105}),
        ('EVT_BUTTON', lambda _: 2 + 2, {'arg': 'a'})
    ]) # yapf: disable
    def test_binds_commands(event_key: str, command, args: dict):
        """should call bind method of node with event and command"""
        node = Mock()
        args = {} if args is None else args
        value = (command, args) if args else command
        setters.bind(node, event_key, value)

        assert node.bind.call_args == call(wx.__dict__[event_key], command, **args)


@fixture
def show_fixture(request):
    sizer = Mock()
    request.cls.node = WxNode(Mock(), Mock(), NodeGlobals({'sizer': sizer}))
    request.cls.sizer = sizer


@mark.usefixtures(show_fixture.__name__)
class ShowTests:
    """setters.show() tests"""

    node: WxNode
    sizer: Mock

    @mark.parametrize('shown, value, called', [
        (True, True, False),
        (False, True, True),
        (True, False, True),
        (False, False, False)
    ]) # yapf: disable
    def test_show(self, shown, value, called):
        """should call Show"""
        self.sizer.IsShown.side_effect = lambda i: shown if self.node.instance == i else not shown

        setters.show(self.node, 'sizer', value)

        if called:
            assert self.sizer.Show.call_args == call(self.node.instance, show = value)
            assert self.sizer.Layout.called
        else:
            assert not self.sizer.Show.called
