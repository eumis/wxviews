#pylint: disable=missing-docstring, invalid-name

from unittest import TestCase
from unittest.mock import Mock, call
from wx import TextCtrl, CheckBox # pylint: disable=E0611
from wx import EVT_TEXT, EVT_CHECKBOX # pylint: disable=E0611
from pyviews.testing import case
from pyviews.core.ioc import register_func
from pyviews.core import XmlAttr, BindingError
from pyviews.core import InheritedDict, ObservableEntity
from pyviews.binding import TwoWaysBinding
from pyviews.compilation import CompiledExpression
from wxviews.node import WidgetNode
from .event import EventBinding, TextTwoWaysRule, CheckBoxTwoWaysRule

register_func('expression', CompiledExpression)

class EventHandlerStub:
    def __init__(self, event):
        self._handler = None
        self._event = event

    def Bind(self, event, handler):
        if event == self._event:
            self._handler = handler

    def Unbind(self, event, handler=None):
        if event == self._event and self._handler == handler:
            self._handler = None

class TextEntryStub(EventHandlerStub, TextCtrl):
    def __init__(self):
        EventHandlerStub.__init__(self, EVT_TEXT)
        self._value = None

    @property
    def Value(self):
        return self._value

    @Value.setter
    def Value(self, value):
        self._value = value

    def ChangeValue(self, value):
        self.Value = value
        if self._handler is not None:
            event = Mock()
            event.GetString.side_effect = lambda: value
            self._handler(event)

class CheckBoxStub(EventHandlerStub, CheckBox):
    def __init__(self):
        EventHandlerStub.__init__(self, EVT_CHECKBOX)
        self._value = None
        self.Value = None

    @property
    def Value(self):
        return self._value

    @Value.setter
    def Value(self, value):
        self._value = value

    def SetValue(self, value):
        self.Value = value
        if self._handler is not None:
            event = Mock()
            event.IsChecked.side_effect = lambda: self.Value
            self._handler(event)

def prop_modifier(node, prop, value):
    setattr(node.instance, prop, value)

class EventBinding_bind_tests(TestCase):
    def test_binds_target_update_to_event(self):
        target, value = (Mock(), 'some value')
        evt_handler, event = (TextEntryStub(), EVT_TEXT)
        binding = EventBinding(target, evt_handler, event)

        binding.bind()
        evt_handler.ChangeValue(value)

        msg = 'should subscribe to event and update target'
        self.assertEqual(call(value), target.on_change.call_args, msg)

    def test_binds_target_update_to_event_with_custom_get_value(self):
        target, value = (Mock(), True)
        evt_handler, event = (CheckBoxStub(), EVT_CHECKBOX)
        binding = EventBinding(target, evt_handler, event, lambda evt: evt.IsChecked())

        binding.bind()
        evt_handler.SetValue(value)

        msg = 'should subscribe to event and update target using passed get_value'
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
    @case({'node': WidgetNode(TextEntryStub(), Mock())}, False)
    @case({'node': WidgetNode(TextEntryStub(), Mock()), 'attr': XmlAttr('Hint')}, False)
    @case({'node': WidgetNode(Mock(), Mock()), 'attr': XmlAttr('Value')}, False)
    @case({'node': WidgetNode(TextEntryStub(), Mock()), 'attr': XmlAttr('Value')}, True)
    def test_checks_instance_type_and_attribute(self, args: dict, expected: bool):
        rule = TextTwoWaysRule()

        actual = rule.suitable(**args)

        msg = 'should be suitable for TextEntry and "Value" property'
        self.assertEqual(expected, actual, msg)

class TextViewModel(ObservableEntity):
    def __init__(self, value=None):
        super().__init__()
        self.text_value = value

class TextTwoWaysRule_apply_tests(TestCase):
    @case('"some value"', {})
    @case('{"some value"}', {})
    @case('val + " value"', {'val': "some"})
    @case('{val + " value"}', {'val': "some"})
    @case('vm.text_value + "text"', {'vm': TextViewModel("some ")})
    @case('{vm.text_value + "text"}', {'vm': TextViewModel("some ")})
    def test_raises_for_invalid_expression(self, expr_body: str, node_globals: dict):
        rule = TextTwoWaysRule()
        node = Mock(node_globals=InheritedDict(node_globals))

        msg = 'should raise error if expression is not observable property or dict value'
        with self.assertRaises(BindingError, msg=msg):
            rule.apply(node=node, expr_body=expr_body,
                       modifier=Mock(), attr=XmlAttr('Value'))

    @case('val', {'val': "value"}, "value")
    @case('{val}', {'val': "value"}, "value")
    @case('vm.text_value', {'vm': TextViewModel("some value")}, 'some value')
    @case('{vm.text_value}', {'vm': TextViewModel("some value")}, 'some value')
    def test_calls_passed_modifier(self, expr_body: str, node_globals: dict, expected_value):
        rule, modifier, xml_attr = (TextTwoWaysRule(), Mock(), XmlAttr('Value'))
        node = Mock(node_globals=InheritedDict(node_globals))

        rule.apply(node=node, expr_body=expr_body, modifier=modifier, attr=xml_attr)

        msg = 'should compile expression and call modifier'
        self.assertEqual(call(node, xml_attr.name, expected_value), modifier.call_args, msg)

    @case(None, 'value')
    @case('', 'value')
    @case('value', 'new value')
    def test_binds_property_to_expression(self, value, new_value):
        rule = TextTwoWaysRule()
        view_model = TextViewModel(value)
        node = Mock(instance=TextEntryStub(), node_globals=InheritedDict({'vm': view_model}))

        rule.apply(node=node, expr_body='vm.text_value', modifier=prop_modifier, attr=XmlAttr('Value'))
        view_model.text_value = new_value

        msg = 'should bind property to expression'
        self.assertEqual(new_value, node.instance.Value, msg)

    def test_binds_expression_to_property(self):
        rule = TextTwoWaysRule()
        value, new_value = ('value', 'new value')
        widget, view_model = TextEntryStub(), TextViewModel(value)
        node = Mock(instance=widget, node_globals=InheritedDict({'vm': view_model}))

        rule.apply(node=node, expr_body='vm.text_value', attr=XmlAttr('Value'), modifier=prop_modifier)
        widget.ChangeValue(new_value)

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

class CheckBoxTwoWaysRule_suitable_tests(TestCase):
    @case({}, False)
    @case({'attr': XmlAttr('Value')}, False)
    @case({'node': WidgetNode(CheckBoxStub(), Mock())}, False)
    @case({'node': WidgetNode(CheckBoxStub(), Mock()), 'attr': XmlAttr('Hint')}, False)
    @case({'node': WidgetNode(Mock(), Mock()), 'attr': XmlAttr('Value')}, False)
    @case({'node': WidgetNode(CheckBoxStub(), Mock()), 'attr': XmlAttr('Value')}, True)
    def test_checks_instance_type_and_attribute(self, args: dict, expected: bool):
        rule = CheckBoxTwoWaysRule()

        actual = rule.suitable(**args)

        msg = 'should be suitable for CheckBox and "Value" property'
        self.assertEqual(expected, actual, msg)

class CheckViewModel(ObservableEntity):
    def __init__(self, value=None):
        super().__init__()
        self.value = value

class CheckBoxTwoWaysRule_apply_tests(TestCase):
    @case('True', {})
    @case('{True}', {})
    @case('val or False', {'val': True})
    @case('{val or False}', {'val': True})
    @case('vm.value or True', {'vm': CheckViewModel(False)})
    @case('{vm.value or True}', {'vm': CheckViewModel(False)})
    def test_raises_for_invalid_expression(self, expr_body: str, node_globals: dict):
        rule = CheckBoxTwoWaysRule()
        node = Mock(node_globals=InheritedDict(node_globals))

        msg = 'should raise error if expression is not observable property or dict value'
        with self.assertRaises(BindingError, msg=msg):
            rule.apply(node=node, expr_body=expr_body,
                       modifier=Mock(), attr=XmlAttr('Value'))

    @case('val', {'val': True}, True)
    @case('{val}', {'val': True}, True)
    @case('{vm.value}', {'vm': CheckViewModel(False)}, False)
    def test_calls_passed_modifier(self, expr_body: str, node_globals: dict, expected_value):
        rule, modifier, xml_attr = (CheckBoxTwoWaysRule(), Mock(), XmlAttr('Value'))
        node = Mock(node_globals=InheritedDict(node_globals))

        rule.apply(node=node, expr_body=expr_body, modifier=modifier, attr=xml_attr)

        msg = 'should compile expression and call modifier'
        self.assertEqual(call(node, xml_attr.name, expected_value), modifier.call_args, msg)

    @case(None, True)
    @case(None, False)
    @case(False, True)
    @case(True, False)
    def test_binds_property_to_expression(self, value, new_value):
        rule = CheckBoxTwoWaysRule()
        view_model = CheckViewModel(value)
        node = Mock(instance=CheckBoxStub(), node_globals=InheritedDict({'vm': view_model}))

        rule.apply(node=node, expr_body='vm.value', modifier=prop_modifier, attr=XmlAttr('Value'))
        view_model.value = new_value

        msg = 'should bind property to expression'
        self.assertEqual(new_value, node.instance.Value, msg)

    @case(False, True)
    @case(True, False)
    def test_binds_expression_to_property(self, value, new_value):
        rule = CheckBoxTwoWaysRule()
        view_model = CheckViewModel(value)
        node = Mock(instance=CheckBoxStub(), node_globals=InheritedDict({'vm': view_model}))

        rule.apply(node=node, expr_body='vm.value', attr=XmlAttr('Value'), modifier=prop_modifier)
        node.instance.SetValue(new_value)

        msg = 'should update expression target on EVT_CHECK event'
        self.assertEqual(new_value, view_model.value, msg)

    def test_adds_binding_to_node(self):
        rule = TextTwoWaysRule()
        node = Mock(node_globals=InheritedDict({'val': 'value'}))

        rule.apply(node=node, expr_body='val', modifier=Mock(), attr=XmlAttr('Value', 'mod'))

        msg = 'should add binding to node'
        self.assertTrue(node.add_binding.called, msg)

        actual_binding = node.add_binding.call_args[0][0]
        self.assertIsInstance(actual_binding, TwoWaysBinding, msg)
