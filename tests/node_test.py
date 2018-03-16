from unittest import TestCase, main
from unittest.mock import Mock, call
from wxviews.node import WxRenderArgs

class WxRenderArgsTests(TestCase):
    def test_init(self):
        xml_node = Mock()
        parent_node = Mock()
        parent = Mock()

        args = WxRenderArgs(xml_node, parent_node, parent)

        msg = 'WxRenderArgs should store passed values in __init__'
        self.assertEqual(args['parent'], parent, msg)
        self.assertEqual(args['sizer'], None, msg)

if __name__ == '__main__':
    main()
