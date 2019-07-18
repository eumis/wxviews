from unittest.mock import Mock, call

import wx
from pytest import mark
from wx.lib.newevent import NewEvent

from wxviews.binding.modifiers import bind

CustomEvent, EVT_CUSTOM_EVENT = NewEvent()


class BindTests:
    """bind() tests"""

    @staticmethod
    @mark.parametrize('event_key, command, args', [
        ('EVT_MOVE', print, None),
        ('EVT_MENU', lambda ev: None, {'id': 105}),
        ('EVT_BUTTON', lambda ev: 2 + 2, {'arg': 'a'})
    ])
    def test_binds_commands(event_key: str, command, args: dict):
        """should call bind method of node with event and command"""
        node = Mock()
        args = {} if args is None else args
        value = (command, args) if args else command
        bind(node, event_key, value)

        assert node.bind.call_args == call(wx.__dict__[event_key], command, **args)
