from unittest.mock import Mock, call, patch

from injectool import add_function_resolver
from pytest import fixture, mark, fail
from pyviews.core import InstanceNode, XmlAttr, Expression
from pyviews.compilation import CompiledExpression
from wxviews.core import pipeline, WxRenderingContext
from wxviews.core.pipeline import setup_instance_node_setter, instance_node_setter, apply_attributes, add_to_sizer

add_function_resolver(Expression, lambda c, p: CompiledExpression(p))


def test_setup_instance_node_setter():
    """setup_instance_node_setter should set attr_setter"""
    node = Mock()

    setup_instance_node_setter(node, WxRenderingContext())

    assert node.attr_setter == instance_node_setter  # pylint: disable=comparison-with-callable


class InstanceNodeSetterTests:
    """instance_node_setter() tests"""

    @staticmethod
    def _data(inst=None):
        return InstanceNode(inst if inst else Mock(), Mock()), 'key', 'value'

    def test_sets_properties(self):
        """should set properties """
        node, key, value = self._data()
        setter = Mock()
        node.properties = {key: Mock(set=setter)}

        instance_node_setter(node, key, value)

        assert setter.call_args == call(value)

    def test_sets_node_property(self):
        """should setup set to node property"""
        node, key, value = self._data()
        setattr(node, key, None)

        instance_node_setter(node, key, value)

        assert getattr(node, key) == value

    def test_sets_instance_property(self):
        """should setup set to instance property"""

        class Instance:
            pass

        inst = Instance()
        node, key, value = self._data(inst)
        setattr(inst, key, None)

        instance_node_setter(node, key, value)

        assert getattr(inst, key) == value


@fixture
def apply_attribute_fixture(request):
    with patch(pipeline.__name__ + '.apply_attribute') as apply_attribute_mock:
        request.cls.apply_attribute = apply_attribute_mock
        yield apply_attribute_mock


@mark.usefixtures('apply_attribute_fixture')
class ApplyAttributesTests:
    """apply_attributes() step tests"""

    @mark.parametrize('attr', [
        XmlAttr('key', 'value', 'init')
    ])
    def test_skip_special_attributes(self, attr):
        """should skip attributes with "init" and "sizer" namespaces"""
        self.apply_attribute.reset_mock()
        node = Mock(xml_node=Mock(attrs=[attr]))

        apply_attributes(node, WxRenderingContext())

        assert not self.apply_attribute.called

    @mark.parametrize('attrs', [
        [XmlAttr('key', 'value')],
        [XmlAttr('key', 'value', ''), XmlAttr('other_key', 1, 'some namespace')]
    ])
    def test_apply_attributes(self, attrs):
        """should apply passed attributes"""
        self.apply_attribute.reset_mock()
        node = Mock(xml_node=Mock(attrs=attrs))

        apply_attributes(node, WxRenderingContext)

        assert self.apply_attribute.call_args_list == [call(node, attr) for attr in attrs]


class AddToSizerTests:
    """add_to_sizer() step tests"""

    @staticmethod
    def _get_mocks(sizer_args=None, node_globals=None):
        sizer_args = sizer_args if sizer_args else {}
        node = Mock(sizer_args=sizer_args, node_globals=node_globals, instace=Mock())
        return node, Mock()

    @mark.parametrize('sizer_args', [
        {},
        {'key': 'value'},
        {'key': 'value', 'one': 1}
    ])
    def test_passes_attr_args(self, sizer_args):
        """should call sizer.Add with node.sizer_args"""
        node, sizer = self._get_mocks(sizer_args)

        add_to_sizer(node, WxRenderingContext({'sizer': sizer}))

        assert sizer.Add.call_args == call(node.instance, **sizer_args)

    def test_skips_if_sizer_missed(self):
        """should skip if sizer is missed"""
        node = self._get_mocks()[0]

        try:
            add_to_sizer(node, WxRenderingContext())
        except BaseException:
            fail()
