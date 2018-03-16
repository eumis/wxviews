from unittest import TestCase, main
from unittest.mock import Mock, call
from wx import App, Frame, Sizer
from pyviews.testing import case
from wxviews.node import WxRenderArgs, ControlNode, FrameNode, AppNode
from wxviews.sizers import SizerNode
from wxviews.rendering import convert_to_node

class CustomSizer(Sizer):
    pass

class RenderingTests(TestCase):
    @case(CustomSizer(), SizerNode)
    @case(App(), AppNode)
    @case(Frame(None), FrameNode)
    @case(Mock(), ControlNode)
    @case({}, ControlNode)
    @case('some object', ControlNode)
    def test_convert_to_node(self, inst, node_class):
        args = WxRenderArgs(Mock())

        node = convert_to_node(inst, args)

        msg = 'convert to node should create right node'
        self.assertTrue(isinstance(node, node_class), msg)

    @case(CustomSizer())
    @case(App())
    @case(Frame(None))
    @case(Mock())
    @case({})
    @case('some object')
    def test_convert_to_node_passes_inst(self, inst):
        args = WxRenderArgs(Mock())

        node = convert_to_node(inst, args)

        msg = 'convert to node should create right node'
        self.assertEqual(node.wx_instance, inst, msg)

if __name__ == '__main__':
    main()
