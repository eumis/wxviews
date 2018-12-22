# pylint: disable=C0103,C0111

from typing import Any
from unittest import TestCase, main
from unittest.mock import Mock, call
from wx import Frame, MenuBar # pylint: disable=E0611
from pyviews import InstanceNode
from pyviews.testing import case
from wxviews.pipeline.menu import set_to_frame, add_menu_properties, set_to_menu_bar

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
    def test_raises_for_parent_not_frame(self, parent: Any):
        node = Mock()

        msg = 'should raise TypeError if parent is not Frame'
        with self.assertRaises(TypeError, msg=msg):
            set_to_menu_bar(node, parent=parent)

    def test_sets_menu_to_bar(self):
        node = Mock(title='some title')
        menu_bar = MenuBarStub()

        set_to_menu_bar(node, parent=menu_bar)

        msg = 'should call SetMenuBar on frame and pass menu bar instance'
        self.assertEqual(menu_bar.Append.call_args, call(node.instance, node.title), msg)

if __name__ == '__main__':
    main()