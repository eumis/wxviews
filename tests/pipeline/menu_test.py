# pylint: disable=C0103,C0111

from typing import Any
from unittest import TestCase, main
from unittest.mock import Mock, call
from wx import Frame # pylint: disable=E0611
from pyviews.testing import case
from wxviews.pipeline.menu import set_to_frame

class NotFrame:
    pass

class FrameStub(Frame):
    def __init__(self):
        self.SetMenuBar = Mock()

class set_to_frame_tests(TestCase):
    @case(Mock())
    @case(NotFrame())
    def test_raises_for_parent_not_frame(self, parent: Any):
        node = Mock()

        msg = 'should raise TypeError if parent is not Frame'
        with self.assertRaises(TypeError, msg=msg):
            set_to_frame(node, parent=parent)

    def test_sets_menu_bar_for_frame(self):
        node = Mock()
        frame = FrameStub()

        set_to_frame(node, parent=frame)

        msg = 'should call SetMenuBar on frame and pass menu bar instance'
        self.assertEqual(frame.SetMenuBar.call_args, call(node.instance), msg)

if __name__ == '__main__':
    main()
