from unittest.mock import Mock

from pytest import fixture, mark
from pyviews.core import XmlAttr

from wxviews.core import WxRenderingContext, get_attr_args


@fixture
def rendering_context_fixture(request):
    request.cls.context = WxRenderingContext()


@mark.usefixtures('rendering_context_fixture')
class WxRenderingContextTests:
    """RenderingContext tests"""

    context: WxRenderingContext

    def test_parent(self):
        """parent property should use key 'parent'"""
        value = Mock()
        init_value = self.context.parent

        self.context.parent = value

        assert init_value is None
        assert self.context.parent == value
        assert self.context['parent'] == value

    def test_sizer(self):
        """sizer property should use key 'sizer'"""
        value = Mock()
        init_value = self.context.sizer

        self.context.sizer = value

        assert init_value is None
        assert self.context.sizer == value
        assert self.context['sizer'] == value

    def test_node_styles(self):
        """node_styles property should use key 'node_styles'"""
        value = Mock()
        init_value = self.context.node_styles

        self.context.node_styles = value

        assert init_value is None
        assert self.context.node_styles == value
        assert self.context['node_styles'] == value


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
    ('init', [XmlAttr('', '{dict({"key":"value"})}', 'init')], {'key': 'value'}),
    ('init', [XmlAttr('', '{dict({"one":"1", "two": 2})}', 'init')], {'one': '1', 'two': 2}),
    ('init', [XmlAttr('', '{dict({"key":1})}', 'init'), XmlAttr('key', '{2}', 'init')], {'key': 2}),
    ('init', [XmlAttr('key', '{2}', 'init'), XmlAttr('', '{dict({"key":1})}', 'init')], {'key': 1})
])
def test_get_attr_args(namespace, attrs, args):
    """should pass parent to instance constructor"""
    xml_node = Mock(attrs=attrs)

    actual = get_attr_args(xml_node, namespace)

    assert actual == args
