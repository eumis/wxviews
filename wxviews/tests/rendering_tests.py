from unittest.mock import Mock, patch

from injectool import add_resolve_function
from pytest import mark
from wx import Sizer, GridSizer
from pyviews.core import XmlAttr, Node, InheritedDict, Expression
from pyviews.compilation import CompiledExpression
from wxviews import rendering
from wxviews.rendering import create_node, get_attr_args
from wxviews.sizers import SizerNode
from wxviews.widgets import WidgetNode

add_resolve_function(Expression, lambda c, p: CompiledExpression(p))


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


class CreateNodeTests:
    """create_node tests"""

    @staticmethod
    def _setup_mocks(get_inst_type: Mock, inst_type, attrs=None):
        attrs = attrs if attrs else []
        xml_node = Mock(attrs=attrs)
        get_inst_type.side_effect = lambda *a, **k: inst_type

        return xml_node

    @mark.parametrize('inst_type', [Node, SomeNode, OtherNode])
    def test_creates_node(self, inst_type):
        """should create node from xml node name and namespace with right type"""
        with patch(rendering.__name__ + '.get_inst_type') as get_inst_type:
            xml_node = self._setup_mocks(get_inst_type, inst_type)

            actual_node = create_node(xml_node)

            assert isinstance(actual_node, inst_type)

    @mark.parametrize('inst_type, init_args', [
        (SomeNode, {}),
        (SomeNode, {'one': 1}),
        (OtherNode, {'parent': Mock(), 'node_globals': InheritedDict(), 'key': 'value'})
    ])
    def test_passes_init_args_to_node(self, inst_type, init_args):
        """should pass arguments to node"""
        with patch(rendering.__name__ + '.get_inst_type') as get_inst_type:
            xml_node = self._setup_mocks(get_inst_type, inst_type)

            actual_node = create_node(xml_node, **init_args)

            assert actual_node.xml_node == xml_node
            assert actual_node.init_args == init_args

    @mark.parametrize('inst_type, node_type', [
        (WxInstance, WidgetNode),
        (OtherWxInstance, WidgetNode),
        (AnySizer, SizerNode),
        (AnyGridSizer, SizerNode)
    ])
    def test_creates_instance(self, inst_type, node_type):
        """should wrap instance to node"""
        with patch(rendering.__name__ + '.get_inst_type') as get_inst_type:
            xml_node = self._setup_mocks(get_inst_type, inst_type)

            actual_node = create_node(xml_node)

            assert isinstance(actual_node.instance, inst_type)
            assert isinstance(actual_node, node_type)

    @mark.parametrize('inst_type, parent', [
        (WxInstance, None),
        (WxInstance, Mock()),
        (OtherWxInstance, None),
        (OtherWxInstance, Mock())
    ])
    def test_passes_parent_to_instance(self, inst_type, parent):
        """should pass parent to instance constructor"""
        with patch(rendering.__name__ + '.get_inst_type') as get_inst_type:
            xml_node = self._setup_mocks(get_inst_type, inst_type)

            actual_node = create_node(xml_node, parent=parent)

            assert actual_node.instance.parent == parent

    @mark.parametrize('inst_type, attrs, args', [
        (WxInstance, [], {}),
        (WxInstance,
         [XmlAttr('key', 'value', 'init')],
         {'key': 'value'}),
        (WxInstance,
         [XmlAttr('key', 'value', 'init'), XmlAttr('one', '{1}', 'init')],
         {'key': 'value', 'one': 1}),
        (OtherWxInstance,
         [XmlAttr('key', '{"v" + "alue"}', 'init'), XmlAttr('one', '1', 'init')],
         {'key': 'value', 'one': '1'}),
        (AnySizer,
         [XmlAttr('key', '{"v" + "alue"}', 'init'), XmlAttr('one', '1', 'init')],
         {'key': 'value', 'one': '1'}),
        (AnyGridSizer,
         [XmlAttr('key', '{"v" + "alue"}', 'init'), XmlAttr('one', '1', 'init')],
         ('value', '1'))
    ])
    def test_passes_init_attrs_to_instance(self, inst_type, attrs, args):
        """should pass parent to instance constructor"""
        with patch(rendering.__name__ + '.get_inst_type') as get_inst_type:
            xml_node = self._setup_mocks(get_inst_type, inst_type, attrs)

            actual_node = create_node(xml_node)

            assert actual_node.instance.init_args == args

    @mark.parametrize('attr', [
        XmlAttr('key', '1'),
        XmlAttr('key', '1', ''),
        XmlAttr('key', '1', 'some_namespace')
    ])
    def test_skips_not_init_attrs(self, attr: XmlAttr):
        """should pass parent to instance constructor"""
        with patch(rendering.__name__ + '.get_inst_type') as get_inst_type:
            xml_node = self._setup_mocks(get_inst_type, WxInstance, [attr])

            actual_node = create_node(xml_node)

            assert actual_node.instance.init_args == {}


@mark.parametrize('namespace, attrs, args', [
    ('init', [], {}),
    ('init', [XmlAttr('key', 'value', 'init')], {'key': 'value'}),
    ('init',
     [XmlAttr('key', 'value', 'init'), XmlAttr('one', '{1}', 'init')],
     {'key': 'value', 'one': 1}),
    ('init',
     [XmlAttr('key', '{"v" + "alue"}', 'init'), XmlAttr('one', '1', 'init')],
     {'key': 'value', 'one': '1'}),
    ('sizer', [XmlAttr('key', 'value', 'sizer')], {'key': 'value'}),
    ('sizer',
     [XmlAttr('key', 'value', 'sizer'), XmlAttr('another key', '{1}', 'init')],
     {'key': 'value'}),
    ('sizer', [XmlAttr('key', 'value', 'init')], {}),
    ('init', [XmlAttr('', '{{"key":"value"}}', 'init')], {'key': 'value'}),
    ('init', [XmlAttr('', '{{"one":"1", "two": 2}}', 'init')], {'one': '1', 'two': 2}),
    ('init', [XmlAttr('', '{{"key":1}}', 'init'), XmlAttr('key', '{2}', 'init')], {'key': 2}),
    ('init', [XmlAttr('key', '{2}', 'init'), XmlAttr('', '{{"key":1}}', 'init')], {'key': 1})
])
def test_get_attr_args(namespace, attrs, args):
    """should pass parent to instance constructor"""
    xml_node = Mock(attrs=attrs)

    actual = get_attr_args(xml_node, namespace)

    assert actual == args
