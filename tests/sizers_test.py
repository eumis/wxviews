from unittest import TestCase, main
from unittest.mock import Mock, call
from wxviews.node import ControlNode
from wxviews.sizers import SizerNode, set_sizer, add_to_sizer

class SizerNodeTests(TestCase):
    def test_wx_instance(self):
        sizer = Mock()
        node = SizerNode(sizer, Mock())

        msg = 'SizerNode should have wx_instance property that returns sizer'
        self.assertEqual(node.wx_instance, sizer, msg)

    def test_get_render_args(self):
        sizer = Mock()
        node = SizerNode(sizer, Mock())
        args = node.get_render_args(Mock())

        msg = 'SizerNode.get_render_args should add sizer to args'
        self.assertEqual(args['sizer'], sizer, msg)

class RenderStepsTests(TestCase):
    def test_set_sizer(self):
        sizer = Mock()
        node = SizerNode(sizer, Mock())
        parent = Mock()

        set_sizer(node, {'sizer': None, 'parent': parent})

        msg = 'set_sizer should call SetSizer on parent if parent is Control'
        self.assertEqual(parent.SetSizer.call_args, call(sizer), msg)

    def test_set_sizer_for_sizer_parent(self):
        node = SizerNode(Mock(), Mock())
        parent = Mock()

        set_sizer(node, {'sizer': Mock(), 'parent': parent})

        msg = 'set_sizer should not call SetSizer on parent if parent is Sizer'
        self.assertFalse(parent.SetSizer.called, msg)

    def test_add_to_sizer(self):
        wx_inst = Mock()
        sizer = Mock()
        node = ControlNode(wx_inst, Mock())
        node.sizer_args = [1, 'value2']
        node.sizer_kwargs = {'key': 'value', 'int_key': 1}

        add_to_sizer(node, {'sizer': sizer})

        msg = 'add_to_sizer should add control to parent sizer'
        expected = call(wx_inst, *node.sizer_args, **node.sizer_kwargs)
        self.assertEqual(sizer.Add.call_args, expected, msg)

if __name__ == '__main__':
    main()
