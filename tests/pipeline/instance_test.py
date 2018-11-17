'''WxNode rendering pipeline tests'''

# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call, patch
from pyviews.core.xml import XmlAttr
from pyviews.testing import case
from wxviews.core.node import WxNode
from wxviews.pipeline.instance import setup_setter, apply_attributes, render_wx_children

class setup_setter_tests(TestCase):
    def _data(self, inst=None):
        return (WxNode(inst if inst else Mock(), None), 'key', 'value')

    def _act(self, node, key, value):
        setup_setter(node)
        node.set_attr(key, value)

    def test_sets_properties(self):
        node, key, value = self._data()
        setter = Mock()
        node.properties = {key:Mock(set=setter)}

        self._act(node, key, value)

        msg = 'setup_setter should setup set to properties'
        self.assertEqual(setter.call_args, call(value), msg)

    def test_sets_node_property(self):
        node, key, value = self._data()
        setattr(node, key, None)

        self._act(node, key, value)

        msg = 'setup_setter should setup set to node property'
        self.assertEqual(getattr(node, key), value, msg)

    def test_sets_instance_property(self):
        class Instance:
            pass
        inst = Instance()
        node, key, value = self._data(inst)
        setattr(inst, key, None)

        self._act(node, key, value)

        msg = 'setup_setter should setup set to instance property'
        self.assertEqual(getattr(inst, key), value, msg)

class apply_attributes_tests(TestCase):
    @patch('wxviews.pipeline.instance.apply_attribute')
    @case(XmlAttr('key', 'value', 'init'))
    def test_skip_init_attributes(self, apply_attribute: Mock, attr):
        node = Mock(xml_node=Mock(attrs=[attr]))

        apply_attributes(node)

        msg = 'should skip attributes with "init" namespace'
        self.assertFalse(apply_attribute.called, msg)

    @patch('wxviews.pipeline.instance.apply_attribute')
    @case([XmlAttr('key', 'value')])
    @case([XmlAttr('key', 'value', ''), XmlAttr('other_key', 1, 'some namespace')])
    def test_apply_attributes(self, apply_attribute: Mock, attrs):
        apply_attribute.reset_mock()
        node = Mock(xml_node=Mock(attrs=attrs))

        apply_attributes(node)

        msg = 'should apply passed attributes'
        self.assertEqual(apply_attribute.call_args_list, [call(node, attr) for attr in attrs], msg)

class render_wx_children_tests(TestCase):
    @patch('wxviews.pipeline.instance.render_children')
    def test_passes_child_args(self, render_children: Mock):
        node = Mock(instance=Mock(), node_globals=Mock())
        expected_args = {'parent': node.instance, 'node_globals': node.node_globals}

        render_wx_children(node)

        msg = 'should pass right child args to render_children'
        self.assertEqual(render_children.call_args, call(node, **expected_args), msg)

if __name__ == '__main__':
    main()
