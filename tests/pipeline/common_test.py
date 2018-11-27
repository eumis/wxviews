'''WxNode rendering pipeline tests'''

# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call, patch
from pyviews.testing import case
from pyviews.core.node import InstanceNode
from pyviews.core.xml import XmlAttr
from wxviews.pipeline.common import instance_node_setter, apply_attributes, add_to_sizer

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

class add_to_sizer_tests(TestCase):
    def _get_mocks(self, attrs=None, node_globals=None):
        attrs = attrs if attrs else []
        xml_node = Mock(attrs=attrs)
        node = Mock(xml_node=xml_node, node_globals=node_globals, instace=Mock())
        return (node, Mock())

    def test_calls_sizer_add(self):
        node, sizer = self._get_mocks()

        add_to_sizer(node, sizer=sizer)

        msg = 'add_to_sizer should call sizer.add for passed node'
        self.assertEqual(sizer.Add.call_args, call(node.instance), msg)

    @case([], {})
    @case([XmlAttr('key', 'value', 'sizer')], {'key': 'value'})
    @case([XmlAttr('key', 'value', 'sizer'), XmlAttr('one', '{1}', 'sizer')],
          {'key': 'value', 'one': 1})
    @case([XmlAttr('key', '{"v" + "alue"}', 'sizer'), XmlAttr('one', '1', 'sizer')],
          {'key': 'value', 'one': '1'})
    @case([XmlAttr('key', 'value', 'sizer'), XmlAttr('another key', '{1}', 'init')],
          {'key': 'value'})
    @case([XmlAttr('key', 'value', 'init')], {})
    def test_passes_attr_args(self, attrs, args):
        node, sizer = self._get_mocks(attrs)

        add_to_sizer(node, sizer=sizer)

        msg = 'add_to_sizer should pass attrs values with namespace "sizer" as args'
        self.assertEqual(sizer.Add.call_args, call(node.instance, **args), msg)

    def test_skips_if_sizer_missed(self):
        node = self._get_mocks()[0]

        try:
            add_to_sizer(node)
        except:
            self.fail('add_to_sizer skip if sizer is missed')

if __name__ == '__main__':
    main()