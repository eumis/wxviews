from unittest.mock import Mock, call

from pytest import mark, fixture
from pyviews.core.observable import InheritedDict
import wx
from wx.lib.newevent import NewEvent
from wxviews.widgets.rendering import WxNode

from wxviews.widgets import setters

CustomEvent, EVT_CUSTOM_EVENT = NewEvent()


class BindTests:
    """setters.show() tests"""

    @staticmethod
    @mark.parametrize('event_key, command, args', [
        ('EVT_MOVE', print, None),
        ('EVT_MENU', lambda _: None, {'id': 105}),
        ('EVT_BUTTON', lambda _: 2 + 2, {'arg': 'a'})
    ])
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
    request.cls.node = WxNode(Mock(), Mock(), InheritedDict({'sizer': sizer}))
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
    ])
    def test_show(self, shown, value, called):
        """should call Show"""
        self.sizer.IsShown.side_effect = lambda i: shown if self.node.instance == i else not shown

        setters.show(self.node, 'sizer', value)

        if called:
            assert self.sizer.Show.call_args == call(self.node.instance, show=value)
            assert self.sizer.Layout.called
        else:
            assert not self.sizer.Show.called
