'''SizerNode tests'''

# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call, patch
from pyviews.testing import case
from wxviews.core.sizers import SizerNode

class SizerNode_destroy_test(TestCase):
    def test_destroys_sizer(self):
        sizer = Mock()
        node = SizerNode(sizer, Mock())

        node.destroy()

        msg = 'destroy should destroy sizer'
        self.assertTrue(sizer.Destroy.called, msg)

if __name__ == '__main__':
    main()
