from typing import Tuple
from unittest.mock import Mock, call, patch

from pytest import fail, fixture, mark
from pyviews.core.xml import XmlAttr

from wxviews.core import pipes
from wxviews.core.pipes import add_to_sizer, apply_attributes
from wxviews.core.rendering import WxRenderingContext
from wxviews.widgets.rendering import WxNode


class TestControl:

    def __init__(self):
        self.node_key = None
        self.instance_key = None


class TestNode(WxNode):

    def __init__(self, widget):
        super().__init__(widget, Mock())
        self.node_key = None


@fixture
def apply_attribute_fixture(request):
    with patch(pipes.__name__ + '.apply_attribute') as apply_attribute_mock:
        request.cls.apply_attribute = apply_attribute_mock
        yield apply_attribute_mock


@mark.usefixtures('apply_attribute_fixture')
class ApplyAttributesTests:
    """apply_attributes() step tests"""

    apply_attribute: Mock

    @mark.parametrize('attr', [XmlAttr('key', 'value', 'init')])
    def test_skip_special_attributes(self, attr):
        """should skip attributes with "init" and "sizer" namespaces"""
        self.apply_attribute.reset_mock()
        node = Mock(xml_node = Mock(attrs = [attr]))

        apply_attributes(node, WxRenderingContext())

        assert not self.apply_attribute.called

    @mark.parametrize('attrs', [
        [XmlAttr('key', 'value')],
        [XmlAttr('key', 'value', ''), XmlAttr('other_key', 'key', 'some namespace')]
    ]) # yapf: disable
    def test_apply_attributes(self, attrs):
        """should apply passed attributes"""
        self.apply_attribute.reset_mock()
        node = Mock(xml_node = Mock(attrs = attrs))

        apply_attributes(node, WxRenderingContext())

        assert self.apply_attribute.call_args_list == [call(node, attr) for attr in attrs]


class AddToSizerTests:
    """add_to_sizer() step tests"""

    @staticmethod
    def _get_mocks(sizer_args = None, node_globals = None) -> Tuple[Mock, Mock]:
        sizer_args = sizer_args if sizer_args else {}
        node = Mock(sizer_args = sizer_args, node_globals = node_globals, instace = Mock())
        return node, Mock()

    @mark.parametrize('sizer_args', [
        {},
        {'key': 'value'},
        {'key': 'value', 'one': 1}
    ]) # yapf: disable
    def test_passes_attr_args(self, sizer_args):
        """should call sizer.Add with node.sizer_args"""
        node, sizer = self._get_mocks(sizer_args)

        add_to_sizer(node, WxRenderingContext({'sizer': sizer}))

        assert sizer.Add.call_args == call(node.sizer_item, **sizer_args)

    def test_skips_if_sizer_missed(self):
        """should skip if sizer is missed"""
        node = self._get_mocks()[0]

        try:
            add_to_sizer(node, WxRenderingContext())
        except BaseException:
            fail()
