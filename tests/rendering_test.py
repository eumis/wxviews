'''Rendering tests'''

# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call, patch
from pyviews.core.xml import XmlAttr
from pyviews.core.node import Node
from pyviews.testing import case
from wxviews.rendering import create_node
from wxviews.core.node import WxNode

class create_node_tests(TestCase):
    def _get_mocks(self, get_inst_type: Mock, attrs=None):
        attrs = attrs if attrs else []
        xml_node = Mock(children=attrs)
        inst_type = Mock()
        get_inst_type.side_effect = lambda *a, **k: inst_type

        return (xml_node, inst_type)

    @patch('wxviews.rendering.create_inst')
    @patch('wxviews.rendering.get_inst_type')
    def test_creates_inst_with_right_type(self, get_inst_type: Mock, create_inst: Mock):
        xml_node, inst_type = self._get_mocks(get_inst_type)

        create_node(xml_node)

        msg = 'should create instance with right type'
        self.assertEqual(create_inst.call_args, call(inst_type, xml_node=xml_node), msg)

    @patch('wxviews.rendering.create_inst')
    @patch('wxviews.rendering.get_inst_type')
    @case({}, [], {})
    @case({'one': 'some value'},
          [XmlAttr('two', '2', 'init')],
          {'one': 'some value', 'two': '2'})
    @case({'one': 1, 'two': 'value'},
          [XmlAttr('two', '{2}', 'init'), XmlAttr('three', '{"v" + "alue"}', 'init')],
          {'one': 1, 'two': 2, 'three': 'value'})
    def test_creates_inst_with_init_args(self, get_inst_type: Mock, create_inst: Mock,
                                         init_args: dict, attrs, expected_args: dict):
        xml_node, inst_type = self._get_mocks(get_inst_type, attrs)
        expected_args = {**expected_args, **{'xml_node': xml_node}}

        create_node(xml_node, **init_args)

        msg = 'should create instance using init_args, attrs with "init" namepspace and xml_node'
        self.assertEqual(create_inst.call_args, call(inst_type, **expected_args), msg)

    @patch('wxviews.rendering.create_inst')
    @patch('wxviews.rendering.get_inst_type')
    @case(XmlAttr('init', '1'))
    @case(XmlAttr('init', '1', ''))
    @case(XmlAttr('init', '1', 'some_namespace'))
    def test_skips_not_init_attrs(self, get_inst_type: Mock, create_inst: Mock, attr: XmlAttr):
        xml_node, inst_type = self._get_mocks(get_inst_type, [attr])

        create_node(xml_node)

        msg = 'should skipe attributes with not "init" namespace'
        self.assertEqual(create_inst.call_args, call(inst_type, xml_node=xml_node), msg)

    @patch('wxviews.rendering.create_inst')
    @patch('wxviews.rendering.get_inst_type')
    @case(Node(None))
    @case(WxNode(None, None))
    def test_returns_created_node(self, get_inst_type: Mock, create_inst: Mock, node):
        xml_node = self._get_mocks(get_inst_type)[0]
        create_inst.side_effect = lambda *a, **k: node

        actual = create_node(xml_node)

        msg = 'should return created node'
        self.assertEqual(actual, node, msg)

    @patch('wxviews.rendering.create_inst')
    @patch('wxviews.rendering.get_inst_type')
    def test_wraps_instance_to_WxNode(self, get_inst_type: Mock, create_inst: Mock):
        xml_node = self._get_mocks(get_inst_type)[0]
        inst = Mock()
        create_inst.side_effect = lambda *a, **k: inst

        actual = create_node(xml_node)

        msg = 'should wrap created instance to WxNode and return this node'
        self.assertEqual(actual.instance, inst, msg)

if __name__ == '__main__':
    main()
