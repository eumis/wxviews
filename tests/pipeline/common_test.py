'''WxNode rendering pipeline tests'''

# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call, patch
from pyviews.testing import case
from pyviews.core.node import InstanceNode
from pyviews.core.xml import XmlAttr
from wxviews.pipeline.common import instance_node_setter, apply_attributes

class instance_node_setter_tests(TestCase):
    def _data(self, inst=None):
        return (InstanceNode(inst if inst else Mock(), None), 'key', 'value')

    def test_sets_properties(self):
        node, key, value = self._data()
        setter = Mock()
        node.properties = {key:Mock(set=setter)}

        instance_node_setter(node, key, value)

        msg = 'setup_setter should setup set to properties'
        self.assertEqual(setter.call_args, call(value), msg)

    def test_sets_node_property(self):
        node, key, value = self._data()
        setattr(node, key, None)

        instance_node_setter(node, key, value)

        msg = 'setup_setter should setup set to node property'
        self.assertEqual(getattr(node, key), value, msg)

    def test_sets_instance_property(self):
        class Instance:
            pass
        inst = Instance()
        node, key, value = self._data(inst)
        setattr(inst, key, None)

        instance_node_setter(node, key, value)

        msg = 'setup_setter should setup set to instance property'
        self.assertEqual(getattr(inst, key), value, msg)

class apply_attributes_tests(TestCase):
    @patch('wxviews.pipeline.common.apply_attribute')
    @case(XmlAttr('key', 'value', 'init'))
    @case(XmlAttr('key', 'value', 'sizer'))
    def test_skip_special_attributes(self, apply_attribute: Mock, attr):
        node = Mock(xml_node=Mock(attrs=[attr]))

        apply_attributes(node)

        msg = 'should skip attributes with "init" and "sizer" namespaces'
        self.assertFalse(apply_attribute.called, msg)

    @patch('wxviews.pipeline.common.apply_attribute')
    @case([XmlAttr('key', 'value')])
    @case([XmlAttr('key', 'value', ''), XmlAttr('other_key', 1, 'some namespace')])
    def test_apply_attributes(self, apply_attribute: Mock, attrs):
        apply_attribute.reset_mock()
        node = Mock(xml_node=Mock(attrs=attrs))

        apply_attributes(node)

        msg = 'should apply passed attributes'
        self.assertEqual(apply_attribute.call_args_list, [call(node, attr) for attr in attrs], msg)

if __name__ == '__main__':
    main()
