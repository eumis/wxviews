# pylint: disable=C0111,C0103

from unittest import TestCase, main
from unittest.mock import Mock, call
from wx import TextCtrl, EVT_TEXT # pylint: disable=E0611
from pyviews.testing import case
from pyviews import InheritedDict
from pyviews.core.xml import XmlAttr
from pyviews.core.binding import BindingError, TwoWaysBinding
from wxviews.core.node import WxNode
from wxviews.core.binding import EventBinding, TextTwoWaysRule

class TextEntryStub(TextCtrl):
    def __init__(self):
        self._handler = None
        self.value = None

    def Bind(self, event, handler):
        if event == EVT_TEXT:
            self._handler = handler

    def Unbind(self, event, handler=None):
        if event == EVT_TEXT and self._handler == handler:
            self._handler = None

    def ChangeValue(self, value):
        self.value = value
        if self._handler is not None:
            event = Mock()
            event.GetString.side_effect = lambda: value
            self._handler(event)

class EventBinding_bind_tests(TestCase):
    def test_binds_target_update_to_event(self):
        target, value = (Mock(), 'some value')
        evt_handler, event = (TextEntryStub(), EVT_TEXT)
        binding = EventBinding(target, evt_handler, event)

        binding.bind()
        evt_handler.ChangeValue(value)

        msg = 'should subscribe to event and update target'
        self.assertEqual(call(value), target.on_change.call_args, msg)

class EventBinding_destroy_tests(TestCase):
    def test_unbinds_event(self):
        target, value = (Mock(), 'some value')
        evt_handler, event = (TextEntryStub(), EVT_TEXT)
        binding = EventBinding(target, evt_handler, event)

        binding.bind()
        binding.destroy()
        evt_handler.ChangeValue(value)

        msg = 'should unsubscribe from event'
        self.assertFalse(target.on_change.called, msg)

class TextTwoWaysRule_suitable_tests(TestCase):
    @case({}, False)
    @case({'attr': XmlAttr('Value')}, False)
    @case({'node': WxNode(TextEntryStub(), Mock())}, False)
    @case({'node': WxNode(TextEntryStub(), Mock()), 'attr': XmlAttr('Hint')}, False)
    @case({'node': WxNode(Mock(), Mock()), 'attr': XmlAttr('Value')}, False)
    @case({'node': WxNode(TextEntryStub(), Mock()), 'attr': XmlAttr('Value')}, True)
    def test_checks_instance_type_and_attribute(self, args: dict, expected: bool):
        rule = TextTwoWaysRule()

        actual = rule.suitable(**args)

        msg = 'should be suitable for TextEntry and "Value" property'
        self.assertEqual(expected, actual, msg)

class TestViewModel:
    def __init__(self, value=None):
        self.text_value = value

class TextTwoWaysRule_apply_tests(TestCase):
    @case('"some value"', {})
    @case('val + " value"', {'val': "some"})
    @case('vm.text_value + "text"', {'vm': TestViewModel("some ")})
    def test_raises_for_invalid_expression(self, expr_body: str, node_globals: dict):
        rule = TextTwoWaysRule()
        node = Mock(node_globals=InheritedDict(node_globals))

        msg = 'should raise error if expression is not observable property or dict value'
        with self.assertRaises(BindingError, msg=msg):
            rule.apply(node=node, expr_body=expr_body,
                       modifier=Mock(), attr=XmlAttr('Value', namespace='somemodifier'))

    @case('val', {'val': "value"}, "value")
    @case('vm.text_value', {'vm': TestViewModel("some value")}, 'some value')
    def test_calls_passed_modifier(self, expr_body: str, node_globals: dict, expected_value):
        rule, modifier, xml_attr = (TextTwoWaysRule(), Mock(), XmlAttr('Value', namespace='somemodifier'))
        node = Mock(node_globals=InheritedDict(node_globals))

        rule.apply(node=node, expr_body=expr_body, modifier=modifier, attr=xml_attr)

        msg = 'should compile expression and call modifier'
        self.assertEqual(call(node, xml_attr.name, expected_value), modifier.call_args, msg)

    @case('val', {'val': "value"}, "value")
    @case('vm.text_value', {'vm': TestViewModel("some value")}, 'some value')
    def test_default_modifier_replaced(self, expr_body: str, node_globals: dict, expected_value):
        rule, modifier, xml_attr = (TextTwoWaysRule(), Mock(), XmlAttr('Value'))
        node = Mock(instance=Mock(), node_globals=InheritedDict(node_globals))

        rule.apply(node=node, expr_body=expr_body, modifier=modifier, attr=xml_attr)

        msg = 'should call ChangeValue method in case modifier is default'
        self.assertEqual(call(expected_value), node.instance.ChangeValue.call_args, msg)

    @case(XmlAttr('Value', namespace='somemodifier'), 'value', 'new value',
          lambda node, modifier: modifier.call_args,
          lambda node, modifier: call(node, 'Value', 'new value'))
    @case(XmlAttr('Value'), 'value', 'new value',
          lambda node, modifier: node.instance.ChangeValue.call_args,
          lambda node, modifier: call('new value'))
    def test_binds_property_to_expression(self, attr, value, new_value, get_actual_call, get_expected_call):
        rule = TextTwoWaysRule()

        property_name, modifier = ('key', Mock())
        node = Mock(instance=Mock(), node_globals=InheritedDict({property_name: value}))

        rule.apply(node=node, expr_body=property_name, modifier=modifier, attr=attr)
        node.instance.ChangeValue.reset_mock()
        modifier.reset_mock()

        node.node_globals[property_name] = new_value

        actual = get_actual_call(node, modifier)
        expected = get_expected_call(node, modifier)

        msg = 'should bind property to expression'
        self.assertEqual(expected, actual, msg)

    def test_binds_expression_to_property(self):
        rule = TextTwoWaysRule()
        value, new_value = ('value', 'new value')
        text_mock, view_model = TextEntryStub(), TestViewModel(value)
        node = Mock(instance=text_mock, node_globals=InheritedDict({'vm': view_model}))

        rule.apply(node=node, expr_body='vm.text_value', attr=XmlAttr('Value'))
        text_mock.ChangeValue(new_value)

        msg = 'should update expression target on EVT_TEXT event'
        self.assertEqual(new_value, view_model.text_value, msg)

    def test_adds_binding_to_node(self):
        rule = TextTwoWaysRule()
        node = Mock(node_globals=InheritedDict({'val': 'value'}))

        rule.apply(node=node, expr_body='val', modifier=Mock(), attr=XmlAttr('Value', 'mod'))

        msg = 'should add binding to node'
        self.assertTrue(node.add_binding.called, msg)

        actual_binding = node.add_binding.call_args[0][0]
        self.assertIsInstance(actual_binding, TwoWaysBinding, msg)

if __name__ == '__main__':
    main()
