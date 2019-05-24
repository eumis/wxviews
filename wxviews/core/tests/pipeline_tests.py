from unittest import TestCase
from unittest.mock import Mock, call, patch

from injectool import register_func
from pyviews.core import InstanceNode, XmlAttr, Expression
from pyviews.compilation import CompiledExpression
from wxviews.core import pipeline
from wxviews.core.pipeline import setup_instance_node_setter, instance_node_setter, apply_attributes, add_to_sizer

register_func(Expression, CompiledExpression)


def test_setup_instance_node_setter():
    """setup_instance_node_setter should set attr_setter"""
    node = Mock()

    setup_instance_node_setter(node)

    assert node.attr_setter == instance_node_setter


class InstanceNodeSetterTests:
    """instance_node_setter() tests"""

    @staticmethod
    def _data(inst=None):
        return InstanceNode(inst if inst else Mock(), None), 'key', 'value'

    def test_sets_properties(self):
        """should set propertyies """
        node, key, value = self._data()
        setter = Mock()
        node.properties = {key: Mock(set=setter)}

        instance_node_setter(node, key, value)

        assert setter.call_args == call(value)

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
    @patch(pipeline.__name__ + '.apply_attribute')
    @case(XmlAttr('key', 'value', 'init'))
    def test_skip_special_attributes(self, apply_attribute: Mock, attr):
        node = Mock(xml_node=Mock(attrs=[attr]))

        apply_attributes(node)

        msg = 'should skip attributes with "init" and "sizer" namespaces'
        self.assertFalse(apply_attribute.called, msg)

    @patch(pipeline.__name__ + '.apply_attribute')
    @case([XmlAttr('key', 'value')])
    @case([XmlAttr('key', 'value', ''), XmlAttr('other_key', 1, 'some namespace')])
    def test_apply_attributes(self, apply_attribute: Mock, attrs):
        apply_attribute.reset_mock()
        node = Mock(xml_node=Mock(attrs=attrs))

        apply_attributes(node)

        msg = 'should apply passed attributes'
        self.assertEqual(apply_attribute.call_args_list, [call(node, attr) for attr in attrs], msg)


class add_to_sizer_tests(TestCase):
    @staticmethod
    def _get_mocks(sizer_args=None, node_globals=None):
        sizer_args = sizer_args if sizer_args else {}
        node = Mock(sizer_args=sizer_args, node_globals=node_globals, instace=Mock())
        return node, Mock()

    @case({})
    @case({'key': 'value'})
    @case({'key': 'value', 'one': 1})
    def test_passes_attr_args(self, sizer_args):
        node, sizer = self._get_mocks(sizer_args)

        add_to_sizer(node, sizer=sizer)

        msg = 'add_to_sizer should call sizer.Add with node.sizer_args'
        self.assertEqual(sizer.Add.call_args, call(node.instance, **sizer_args), msg=msg)

    def test_skips_if_sizer_missed(self):
        node = self._get_mocks()[0]

        try:
            add_to_sizer(node)
        except:
            self.fail('add_to_sizer skip if sizer is missed')
