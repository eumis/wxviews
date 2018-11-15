'''WxNode rendering pipeline tests'''

# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call, patch
from pyviews.core.xml import XmlAttr
from pyviews.core.observable import InheritedDict
from pyviews.testing import case
from wxviews.core.node import WxNode
from wxviews.rendering.instance import init_instance, setup_setter
from wxviews.rendering.instance import apply_attributes, render_wx_children

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
    def test_skip_not_init_attrs(self, attr):
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
        node, key, value = self._data()
        class Instance:
            pass
        inst = Instance()
        node.init(inst)
        setattr(inst, key, None)

        self._act(node, key, value)

        msg = 'setup_setter should setup set to instance property'
        self.assertEqual(getattr(inst, key), value, msg)

class apply_attributes_tests(TestCase):
    @patch('wxviews.rendering.instance.apply_attribute')
    @case(XmlAttr('key', 'value', 'init'))
    def test_skip_init_attributes(self, apply_attribute: Mock, attr):
        node = Mock(xml_node=Mock(attrs=[attr]))

        apply_attributes(node)

        msg = 'should skip attributes with "init" namespace'
        self.assertFalse(apply_attribute.called, msg)

    @patch('wxviews.rendering.instance.apply_attribute')
    @case([XmlAttr('key', 'value')])
    @case([XmlAttr('key', 'value', ''), XmlAttr('other_key', 1, 'some namespace')])
    def test_apply_attributes(self, apply_attribute: Mock, attrs):
        apply_attribute.reset_mock()
        node = Mock(xml_node=Mock(attrs=attrs))

        apply_attributes(node)

        msg = 'should apply passed attributes'
        self.assertEqual(apply_attribute.call_args_list, [call(node, attr) for attr in attrs], msg)

class render_wx_children_tests(TestCase):
    @patch('wxviews.rendering.instance.render_children')
    def test_passes_child_args(self, render_children: Mock):
        node = Mock(instance=Mock(), node_globals=Mock())
        expected_args = {'parent': node.instance, 'node_globals': node.node_globals}

        render_wx_children(node)

        msg = 'should pass right child args to render_children'
        self.assertEqual(render_children.call_args, call(node, **expected_args), msg)

if __name__ == '__main__':
    main()
