from typing import Any
from unittest.mock import Mock, call

from pytest import mark, raises
from pyviews.core.xml import XmlAttr, XmlNode
from wx import Frame, Menu, MenuBar

from wxviews.core.rendering import WxRenderingContext
from wxviews.menus import set_to_frame, set_to_menu, set_to_menu_bar


class EmptyClass:
    pass


class FrameStub(Frame):

    def __init__(self):
        self.SetMenuBar = Mock()


class SetToFrameTests:
    """set_to_frame tests"""

    @staticmethod
    @mark.parametrize('parent', [Mock(), EmptyClass()])
    def test_raises_for_parent_not_frame(parent: Any):
        """should raise TypeError if parent is not Frame"""
        node = Mock()

        with raises(TypeError):
            set_to_frame(node, WxRenderingContext({'parent': parent}))

    @staticmethod
    def test_sets_menu_bar_to_frame():
        """should call SetMenuBar on frame and pass menu bar instance"""
        node = Mock()
        frame = FrameStub()

        set_to_frame(node, WxRenderingContext({'parent': frame}))

        assert frame.SetMenuBar.call_args == call(node.instance)


class MenuBarStub(MenuBar):

    def __init__(self):
        self.Append = Mock()


class SetToMenuBarTests:
    """set_to_menu_bar tests"""

    @staticmethod
    @mark.parametrize('parent', [Mock(), EmptyClass()])
    def test_raises_for_invalid_parent(parent: Any):
        """should raise TypeError if parent is not Frame"""
        node = Mock()

        with raises(TypeError):
            set_to_menu_bar(node, WxRenderingContext({'parent': parent}))

    @staticmethod
    def test_sets_menu_to_bar():
        """should call Append on menu baar and pass menu instance"""
        title = 'some title'
        node = Mock(properties = {}, xml_node = XmlNode('wx', 'Menu', attrs = [XmlAttr('title', title)]))
        menu_bar = MenuBarStub()

        set_to_menu_bar(node, WxRenderingContext({'parent': menu_bar}))

        assert menu_bar.Append.call_args == call(node.instance, title)


class MenuStub(Menu):

    def __init__(self):
        self.Append = Mock()


class SetToMenuTests:
    """set_to_menu tests"""

    @staticmethod
    @mark.parametrize('parent', [Mock(), EmptyClass()])
    def test_raises_for_invalid_parent(parent: Any):
        """should raise TypeError if parent is not Frame"""
        node = Mock()

        with raises(TypeError):
            set_to_menu(node, WxRenderingContext({'parent': parent}))

    @staticmethod
    def test_sets_item_to_menu():
        """should call Append menu and pass item instance"""
        node = Mock()
        menu = MenuStub()

        set_to_menu(node, WxRenderingContext({'parent': menu}))

        assert menu.Append.call_args == call(node.instance)
