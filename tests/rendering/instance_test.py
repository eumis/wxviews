'''WxNode rendering pipeline tests'''

# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call
from pyviews.core.xml import XmlAttr
from pyviews.core.observable import InheritedDict
from pyviews.testing import case
from wxviews.core.node import WxNode
from wxviews.rendering.instance import init_instance, setup_setter

class init_instance_tests(TestCase):
    def test_creates_instance(self):
        node = Mock(xml_node=Mock(children=[]))
        instance = Mock()
        instance_type = Mock(return_value=instance)

        init_instance(node, instance_type=instance_type)

        msg = 'should create entity of instance_type and pass it to WxNode.init'
        self.assertEqual(node.init.call_args, call(instance), msg)

    @case(None)
    @case(Mock())
    def test_passes_parent(self, parent):
        node = Mock(xml_node=Mock(children=[]))
        instance_type = Mock()

        init_instance(node, instance_type=instance_type, parent=parent)

        msg = 'should pass parent to instance_type constructor'
        self.assertEqual(instance_type.call_args, call(parent), msg)

    @case([XmlAttr('one', '1', 'init')], {'one': '1'}, {})
    @case([XmlAttr('one', '{1 + 1}', 'init')], {'one': 2}, {})
    @case([XmlAttr('value', '{value}', 'init')], {'value': 2}, {'value': 2})
    @case([XmlAttr('one', '1', 'init'), XmlAttr('two', '{1 + 1}', 'init')], {'one': '1', 'two': 2}, {})
    def test_passes_init_attrs(self, attrs, expected_kwargs: dict, node_globals: dict):
        node = Mock(xml_node=Mock(children=attrs), node_globals=InheritedDict(node_globals))
        instance_type = Mock()

        init_instance(node, instance_type=instance_type)

        msg = 'should pass attributes with '
        self.assertEqual(instance_type.call_args, call(None, **expected_kwargs), msg)

    @case(XmlAttr('one', '1', None))
    @case(XmlAttr('one', '{1 + 1}', ''))
    @case(XmlAttr('value', '{value}', 'wxviews.import_globa'))
    def test_should_skip_not_init_attrs(self, attr):
        node = Mock(xml_node=Mock(children=[attr]))
        instance_type = Mock()

        init_instance(node, instance_type=instance_type)

        msg = 'should skip not init attrs'
        self.assertEqual(instance_type.call_args, call(None), msg)

class setup_setter_tests(TestCase):
    def _data(self):
        return (WxNode(None), 'key', 'value')

    def _act(self, node, key, value):
        setup_setter(node)
        node.set_attr(key, value)

    def test_setup_setter_sets_properties(self):
        node, key, value = self._data()
        setter = Mock()
        node.properties = {key:Mock(set=setter)}

        self._act(node, key, value)

        msg = 'setup_setter should setup set to properties'
        self.assertEqual(setter.call_args, call(value), msg)

    def test_setup_setter_sets_node_property(self):
        node, key, value = self._data()
        setattr(node, key, None)

        self._act(node, key, value)

        msg = 'setup_setter should setup set to node property'
        self.assertEqual(getattr(node, key), value, msg)

    def test_setup_setter_sets_instance_property(self):
        node, key, value = self._data()
        class Instance:
            pass
        inst = Instance()
        node.init(inst)
        setattr(inst, key, None)

        self._act(node, key, value)

        msg = 'setup_setter should setup set to instance property'
        self.assertEqual(getattr(inst, key), value, msg)

if __name__ == '__main__':
    main()
