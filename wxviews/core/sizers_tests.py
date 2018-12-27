'''SizerNode tests'''

# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call
from wxviews.core.sizers import SizerNode

class SizerNode_destroy_test(TestCase):
    def test_removes_sizer_from_parent(self):
        parent = Mock()
        node = SizerNode(Mock(), Mock(), parent=parent)

        node.destroy()

        msg = 'should remove sizer from parent'
        self.assertEqual(parent.SetSizer.call_args, call(None, True), msg)

    def test_do_nothing_if_has_parent_sizer(self):
        parent = Mock()
        node = SizerNode(Mock(), Mock(), parent=parent, sizer=Mock())

        node.destroy()

        msg = 'should do nothing if has parent sizer'
        self.assertFalse(parent.SetSizer.called, msg)

if __name__ == '__main__':
    main()
