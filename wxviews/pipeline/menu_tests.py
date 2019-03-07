# pylint: disable=C0103,C0111

from typing import Any
from unittest import TestCase
from unittest.mock import Mock, call
from wx import Frame, MenuBar, Menu # pylint: disable=E0611
from pyviews.core import InstanceNode, Property
from pyviews.testing import case
from .menu import set_to_frame, add_menu_properties, set_to_menu_bar, set_to_menu

class EmptyClass:
    pass

class FrameStub(Frame):
    def __init__(self):
        self.SetMenuBar = Mock()

class set_to_frame_tests(TestCase):
    @case(Mock())
    @case(EmptyClass())
    def test_raises_for_parent_not_frame(self, parent: Any):
        node = Mock()

        msg = 'should raise TypeError if parent is not Frame'
        with self.assertRaises(TypeError, msg=msg):
            set_to_frame(node, parent=parent)

    def test_sets_menu_bar_to_frame(self):
        node = Mock()
        frame = FrameStub()

        set_to_frame(node, parent=frame)

        msg = 'should call SetMenuBar on frame and pass menu bar instance'
        self.assertEqual(frame.SetMenuBar.call_args, call(node.instance), msg)

class add_menu_properties_tests(TestCase):
    @case('title')
    def test_adds_property(self, prop: str):
        node = InstanceNode(Mock(), Mock())

        add_menu_properties(node)

        msg = 'should add {0} property for menu node'.format(prop)
        self.assertTrue(prop in node.properties, msg)
        self.assertEqual(prop, node.properties[prop].name)

class MenuBarStub(MenuBar):
    def __init__(self):
        self.Append = Mock()

class set_to_menu_bar_tests(TestCase):
    @case(Mock())
    @case(EmptyClass())
    def test_raises_for_parent_not_MenuBar(self, parent: Any):
        node = Mock()

        msg = 'should raise TypeError if parent is not Frame'
        with self.assertRaises(TypeError, msg=msg):
            set_to_menu_bar(node, parent=parent)

    def test_sets_menu_to_bar(self):
        title = 'some title'
        node = Mock(properties={})
        node.properties['title'] = Property('title')
        node.properties['title'].set(title)
        menu_bar = MenuBarStub()

        set_to_menu_bar(node, parent=menu_bar)

        msg = 'should call Append on menu baar and pass menu instance'
        self.assertEqual(menu_bar.Append.call_args, call(node.instance, title), msg)

class MenuStub(Menu):
    def __init__(self):
        self.Append = Mock()

class set_to_menu_tests(TestCase):
    @case(Mock())
    @case(EmptyClass())
    def test_raises_for_parent_not_Menu(self, parent: Any):
        node = Mock()

        msg = 'should raise TypeError if parent is not Frame'
        with self.assertRaises(TypeError, msg=msg):
            set_to_menu(node, parent=parent)

    def test_sets_item_to_menu(self):
        node = Mock()
        menu = MenuStub()

        set_to_menu(node, parent=menu)

        msg = 'should call Appendon menu and pass item instance'
        self.assertEqual(menu.Append.call_args, call(node.instance), msg)
