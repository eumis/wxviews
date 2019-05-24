from unittest.mock import Mock, call

import wx
from pytest import mark

from wxviews.binding.modifiers import bind


class BindTests:
    """bind() tests"""

    @staticmethod
    @mark.parametrize('event_key, command', [
        ('EVT_MOVE', print),
        ('EVT_BUTTON', lambda ev: 2 + 2),
        ('EVT_SHOW', lambda ev: None)
    ])
    def test_binds_commands(event_key: str, command):
        """should call bind method of node with event and command"""
        node = Mock()
        bind(node, event_key, command)

        assert node.bind.call_args == call(wx.__dict__[event_key], command)

    @staticmethod
    @mark.parametrize('event_key, command, args', [
        ('EVT_MENU', lambda ev: None, {'id': 105}),
        ('EVT_BUTTON', lambda ev: 2 + 2, {'arg': 'a'})
    ])
    def test_binds_commands_with_args(event_key: str, command, args: dict):
        """should call bind method of node with event and command"""
        node = Mock()
        bind(node, event_key, (command, args))

        assert node.bind.call_args == call(wx.__dict__[event_key], command, **args)
