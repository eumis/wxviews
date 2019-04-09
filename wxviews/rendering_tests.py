# pylint: disable=C0111,C0103, W0231

from unittest import TestCase, main
from unittest.mock import Mock, patch
from wx import Sizer, GridSizer # pylint: disable=E0611
from pyviews.core import XmlAttr, Node, InheritedDict
from pyviews.core.ioc import register_func
from pyviews.compilation import CompiledExpression
from pyviews.testing import case
from wxviews.node import SizerNode, WidgetNode
from wxviews import rendering
from wxviews.rendering import create_node, get_attr_args

register_func('expression', CompiledExpression)

class SomeNode(Node):
    def __init__(self, xml_node, **init_args):
        self._xml_node = xml_node
        self.init_args = init_args

class OtherNode(WidgetNode):
    def __init__(self, xml_node, **init_args):
        self._xml_node = xml_node
        self.init_args = init_args

class WxInstance:
    def __init__(self, parent, **init_args):
        self.parent = parent
        self.init_args = init_args

class OtherWxInstance:
    def __init__(self, parent, **init_args):
        self.parent = parent
        self.init_args = init_args

class AnySizer(Sizer):
    def __init__(self, **init_args):
        self.init_args = init_args

class AnyGridSizer(GridSizer):
    def __init__(self, *init_args):
        self.init_args = init_args

class create_node_tests(TestCase):
    def _setup_mocks(self, get_inst_type: Mock, inst_type, attrs=None):
        attrs = attrs if attrs else []
        xml_node = Mock(attrs=attrs)
        get_inst_type.side_effect = lambda *a, **k: inst_type

        return xml_node

    @patch(rendering.__name__ + '.get_inst_type')
    @case(Node)
    @case(SomeNode)
    @case(OtherNode)
    def test_creates_node(self, get_inst_type: Mock, inst_type):
        xml_node = self._setup_mocks(get_inst_type, inst_type)

        actual_node = create_node(xml_node)

        msg = 'should create node from xml node name and namespace with right type'
        self.assertTrue(isinstance(actual_node, inst_type), msg)

    @patch(rendering.__name__ + '.get_inst_type')
    @case(SomeNode, {})
    @case(SomeNode, {'one': 1})
    @case(OtherNode, {'parent': Mock(), 'node_globals': InheritedDict(), 'key': 'value'})
    def test_passes_init_args_to_node(self, get_inst_type: Mock, inst_type, init_args):
        xml_node = self._setup_mocks(get_inst_type, inst_type)

        actual_node = create_node(xml_node, **init_args)

        msg = 'should pass xml_node as argument'
        self.assertEqual(actual_node.xml_node, xml_node, msg)

        msg = 'should pass init_args'
        self.assertEqual(actual_node.init_args, init_args, msg)

    @patch(rendering.__name__ + '.get_inst_type')
    @case(WxInstance, WidgetNode)
    @case(OtherWxInstance, WidgetNode)
    @case(AnySizer, SizerNode)
    @case(AnyGridSizer, SizerNode)
    def test_creates_instance(self, get_inst_type: Mock, inst_type, node_type):
        xml_node = self._setup_mocks(get_inst_type, inst_type)

        actual_node = create_node(xml_node)

        msg = 'should wrap instance to node'
        self.assertTrue(isinstance(actual_node.instance, inst_type), msg)

        msg = 'should wrap instance to right instance node'
        self.assertTrue(isinstance(actual_node, node_type), msg)

    @patch(rendering.__name__ + '.get_inst_type')
    @case(WxInstance, None)
    @case(WxInstance, Mock())
    @case(OtherWxInstance, None)
    @case(OtherWxInstance, Mock())
    def test_passes_parent_to_instance(self, get_inst_type: Mock, inst_type, parent):
        xml_node = self._setup_mocks(get_inst_type, inst_type)

        actual_node = create_node(xml_node, parent=parent)

        msg = 'should pass parent to instance constructor'
        self.assertEqual(actual_node.instance.parent, parent, msg)

    @patch(rendering.__name__ + '.get_inst_type')
    @case(WxInstance, [], {})
    @case(WxInstance,
          [XmlAttr('key', 'value', 'init')],
          {'key': 'value'})
    @case(WxInstance,
          [XmlAttr('key', 'value', 'init'), XmlAttr('one', '{1}', 'init')],
          {'key': 'value', 'one': 1})
    @case(OtherWxInstance,
          [XmlAttr('key', '{"v" + "alue"}', 'init'), XmlAttr('one', '1', 'init')],
          {'key': 'value', 'one': '1'})
    @case(AnySizer,
          [XmlAttr('key', '{"v" + "alue"}', 'init'), XmlAttr('one', '1', 'init')],
          {'key': 'value', 'one': '1'})
    @case(AnyGridSizer,
          [XmlAttr('key', '{"v" + "alue"}', 'init'), XmlAttr('one', '1', 'init')],
          ('value', '1'))
    def test_passes_init_attrs_to_instance(self, get_inst_type: Mock, inst_type, attrs, args):
        xml_node = self._setup_mocks(get_inst_type, inst_type, attrs)

        actual_node = create_node(xml_node)

        msg = 'should pass parent to instance constructor'
        self.assertEqual(actual_node.instance.init_args, args, msg)

    @patch(rendering.__name__ + '.get_inst_type')
    @case(XmlAttr('key', '1'))
    @case(XmlAttr('key', '1', ''))
    @case(XmlAttr('key', '1', 'some_namespace'))
    def test_skips_not_init_attrs(self, get_inst_type: Mock, attr: XmlAttr):
        xml_node = self._setup_mocks(get_inst_type, WxInstance, [attr])

        actual_node = create_node(xml_node)

        msg = 'should pass parent to instance constructor'
        self.assertDictEqual(actual_node.instance.init_args, {}, msg)

class get_attr_args_tests(TestCase):
    @case('init', [], {})
    @case('init', [XmlAttr('key', 'value', 'init')], {'key': 'value'})
    @case('init',
          [XmlAttr('key', 'value', 'init'), XmlAttr('one', '{1}', 'init')],
          {'key': 'value', 'one': 1})
    @case('init',
          [XmlAttr('key', '{"v" + "alue"}', 'init'), XmlAttr('one', '1', 'init')],
          {'key': 'value', 'one': '1'})
    @case('sizer', [XmlAttr('key', 'value', 'sizer')], {'key': 'value'})
    @case('sizer',
          [XmlAttr('key', 'value', 'sizer'), XmlAttr('another key', '{1}', 'init')],
          {'key': 'value'})
    @case('sizer', [XmlAttr('key', 'value', 'init')], {})
    @case('init', [XmlAttr('', '{{"key":"value"}}', 'init')], {'key': 'value'})
    @case('init', [XmlAttr('', '{{"one":"1", "two": 2}}', 'init')], {'one': '1', 'two': 2})
    @case('init', [XmlAttr('', '{{"key":1}}', 'init'), XmlAttr('key', '{2}', 'init')], {'key': 2})
    @case('init', [XmlAttr('key', '{2}', 'init'), XmlAttr('', '{{"key":1}}', 'init')], {'key': 1})
    def test_returns_attr_with_values_with_passed_namespace(self, namespace, attrs, args):
        xml_node = Mock(attrs=attrs)

        actual = get_attr_args(xml_node, namespace)

        msg = 'should pass parent to instance constructor'
        self.assertDictEqual(actual, args, msg)

if __name__ == '__main__':
    main()
