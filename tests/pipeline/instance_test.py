'''WxNode rendering pipeline tests'''

# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call, patch
from pyviews.testing import case
from pyviews.core.xml import XmlAttr
from wxviews.pipeline.common import instance_node_setter
from wxviews.pipeline.instance import setup_setter, render_wx_children, add_to_sizer

class setup_setter_tests(TestCase):
    def test_sets_instance_property(self):
        node = Mock()
        setup_setter(node)

        msg = 'setup_setter should set instance_node_setter'
        self.assertEqual(node.attr_setter, instance_node_setter, msg)

class render_wx_children_tests(TestCase):
    @patch('wxviews.pipeline.instance.render_children')
    def test_passes_child_args(self, render_children: Mock):
        node = Mock(instance=Mock(), node_globals=Mock())
        sizer = Mock()
        expected_args = {
            'parent': node.instance,
            'node_globals': node.node_globals,
            'sizer': sizer
        }

        render_wx_children(node, sizer=sizer)

        msg = 'should pass right child args to render_children'
        self.assertEqual(render_children.call_args, call(node, **expected_args), msg)

class add_to_sizer_tests(TestCase):
    def _get_mocks(self, attrs=None, node_globals=None):
        attrs = attrs if attrs else []
        xml_node = Mock(attrs=attrs)
        return (Mock(xml_node=xml_node, node_globals=node_globals), Mock())

    def test_calls_sizer_add(self):
        node, sizer = self._get_mocks()

        add_to_sizer(node, sizer=sizer)

        msg = 'add_to_sizer should call sizer.add for passed node'
        self.assertEqual(sizer.Add.call_args, call(node), msg)

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
        self.assertEqual(sizer.Add.call_args, call(node, **args), msg)

    def test_skips_if_sizer_missed(self):
        node = self._get_mocks()[0]

        try:
            add_to_sizer(node)
        except:
            self.fail('add_to_sizer skip if sizer is missed')

if __name__ == '__main__':
    main()
