from unittest.mock import Mock, call

from injectool import add_function_resolver
from pytest import mark, raises
from wx import TextCtrl, CheckBox
from wx import EVT_TEXT, EVT_CHECKBOX
from pyviews.compilation import CompiledExpression
from pyviews.core import XmlAttr, BindingError, Expression
from pyviews.core import InheritedDict, ObservableEntity
from pyviews.binding import TwoWaysBinding
from wxviews.binding.event import EventBinding, TextTwoWaysRule, CheckBoxTwoWaysRule
from wxviews.widgets import WidgetNode

add_function_resolver(Expression, lambda c, p: CompiledExpression(p))


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


class EventBindingTests:
    """EventBinding class tests"""

    @staticmethod
    def test_binds_target_update_to_event():
        """bind() should subscribe to event and update target"""
        target, value = (Mock(), 'some value')
        evt_handler, event = (TextEntryStub(), EVT_TEXT)
        binding = EventBinding(target, evt_handler, event)

        binding.bind()

        evt_handler.ChangeValue(value)
        assert call(value) == target.on_change.call_args

    @staticmethod
    def test_binds_target_update_to_event_with_custom_get_value():
        """bind() should subscribe to event and update target using passed get_value"""
        target, value = (Mock(), True)
        evt_handler, event = (CheckBoxStub(), EVT_CHECKBOX)
        binding = EventBinding(target, evt_handler, event, lambda evt: evt.IsChecked())

        binding.bind()

        evt_handler.SetValue(value)
        assert call(value) == target.on_change.call_args

    @staticmethod
    def test_destroy():
        """should unsubscribe from event"""
        target, value = (Mock(), 'some value')
        evt_handler, event = (TextEntryStub(), EVT_TEXT)
        binding = EventBinding(target, evt_handler, event)
        binding.bind()

        binding.destroy()

        evt_handler.ChangeValue(value)
        assert not target.on_change.called


class TextViewModel(ObservableEntity):
    def __init__(self, value=None):
        super().__init__()
        self.text_value = value


class TextTwoWaysRuleTests:
    """TextTwoWaysRule class tests"""

    @staticmethod
    @mark.parametrize('args, expected', [
        ({}, False),
        ({'attr': XmlAttr('Value')}, False),
        ({'node': WidgetNode(TextEntryStub(), Mock())}, False),
        ({'node': WidgetNode(TextEntryStub(), Mock()), 'attr': XmlAttr('Hint')}, False),
        ({'node': WidgetNode(Mock(), Mock()), 'attr': XmlAttr('Value')}, False),
        ({'node': WidgetNode(TextEntryStub(), Mock()), 'attr': XmlAttr('Value')}, True)
    ])
    def test_suitable(args: dict, expected: bool):
        """should be suitable for TextEntry and "Value" property"""
        rule = TextTwoWaysRule()

        actual = rule.suitable(**args)

        assert expected == actual

    @staticmethod
    @mark.parametrize('expr_body, node_globals', [
        ('"some value"', {}),
        ('{"some value"}', {}),
        ('val + " value"', {'val': "some"}),
        ('{val + " value"}', {'val': "some"}),
        ('vm.text_value + "text"', {'vm': TextViewModel("some ")}),
        ('{vm.text_value + "text"}', {'vm': TextViewModel("some ")})
    ])
    def test_apply_raises(expr_body: str, node_globals: dict):
        """apply() should raise error if expression is not observable property or dict value"""
        rule = TextTwoWaysRule()
        node = Mock(node_globals=InheritedDict(node_globals))

        with raises(BindingError):
            rule.apply(node=node, expr_body=expr_body,
                       modifier=Mock(), attr=XmlAttr('Value'))

    @staticmethod
    @mark.parametrize('expr_body, node_globals, expected_value', [
        ('val', {'val': "value"}, "value"),
        ('{val}', {'val': "value"}, "value"),
        ('vm.text_value', {'vm': TextViewModel("some value")}, 'some value'),
        ('{vm.text_value}', {'vm': TextViewModel("some value")}, 'some value')
    ])
    def test_calls_modifier(expr_body: str, node_globals: dict, expected_value):
        """apply() should compile expression and call modifier"""
        rule, modifier, xml_attr = (TextTwoWaysRule(), Mock(), XmlAttr('Value'))
        node = Mock(node_globals=InheritedDict(node_globals))

        rule.apply(node=node, expr_body=expr_body, modifier=modifier, attr=xml_attr)

        assert call(node, xml_attr.name, expected_value) == modifier.call_args

    @staticmethod
    @mark.parametrize('value, new_value', [
        (None, 'value'),
        ('', 'value'),
        ('value', 'new value')
    ])
    def test_binds_property_to_expression(value, new_value):
        """apply() should bind property to expression"""
        rule = TextTwoWaysRule()
        view_model = TextViewModel(value)
        node = Mock(instance=TextEntryStub(), node_globals=InheritedDict({'vm': view_model}))

        rule.apply(node=node, expr_body='vm.text_value', modifier=prop_modifier, attr=XmlAttr('Value'))
        view_model.text_value = new_value

        assert new_value == node.instance.Value

    @staticmethod
    def test_binds_expression_to_property():
        """apply() should update expression target on EVT_TEXT event"""
        rule = TextTwoWaysRule()
        value, new_value = ('value', 'new value')
        widget, view_model = TextEntryStub(), TextViewModel(value)
        node = Mock(instance=widget, node_globals=InheritedDict({'vm': view_model}))

        rule.apply(node=node, expr_body='vm.text_value', attr=XmlAttr('Value'), modifier=prop_modifier)
        widget.ChangeValue(new_value)

        assert new_value == view_model.text_value

    @staticmethod
    def test_adds_binding_to_node():
        """apply() should add binding to node"""
        rule = TextTwoWaysRule()
        node = Mock(node_globals=InheritedDict({'val': 'value'}))

        rule.apply(node=node, expr_body='val', modifier=Mock(), attr=XmlAttr('Value', 'mod'))
        actual_binding = node.add_binding.call_args[0][0]

        assert node.add_binding.called
        assert isinstance(actual_binding, TwoWaysBinding)


class CheckViewModel(ObservableEntity):
    def __init__(self, value=None):
        super().__init__()
        self.value = value


class CheckBoxTwoWaysRuleTests:
    """CheckBoxTwoWaysRule class tests"""

    @staticmethod
    @mark.parametrize('args, expected', [
        ({}, False),
        ({'attr': XmlAttr('Value')}, False),
        ({'node': WidgetNode(CheckBoxStub(), Mock())}, False),
        ({'node': WidgetNode(CheckBoxStub(), Mock()), 'attr': XmlAttr('Hint')}, False),
        ({'node': WidgetNode(Mock(), Mock()), 'attr': XmlAttr('Value')}, False),
        ({'node': WidgetNode(CheckBoxStub(), Mock()), 'attr': XmlAttr('Value')}, True)
    ])
    def test_suitable(args: dict, expected: bool):
        """should be suitable for CheckBox and "Value" property"""
        rule = CheckBoxTwoWaysRule()

        actual = rule.suitable(**args)

        assert expected == actual

    @staticmethod
    @mark.parametrize('expr_body, node_globals', [
        ('True', {}),
        ('{True}', {}),
        ('val or False', {'val': True}),
        ('{val or False}', {'val': True}),
        ('vm.value or True', {'vm': CheckViewModel(False)}),
        ('{vm.value or True}', {'vm': CheckViewModel(False)})
    ])
    def test_apply_raises(expr_body: str, node_globals: dict):
        """should raise error if expression is not observable property or dict value"""
        rule = CheckBoxTwoWaysRule()
        node = Mock(node_globals=InheritedDict(node_globals))

        with raises(BindingError):
            rule.apply(node=node, expr_body=expr_body,
                       modifier=Mock(), attr=XmlAttr('Value'))

    @staticmethod
    @mark.parametrize('expr_body, node_globals, expected_value', [
        ('val', {'val': True}, True),
        ('{val}', {'val': True}, True),
        ('{vm.value}', {'vm': CheckViewModel(False)}, False)
    ])
    def test_calls_passed_modifier(expr_body: str, node_globals: dict, expected_value):
        """apply() should compile expression and call modifier"""
        rule, modifier, xml_attr = (CheckBoxTwoWaysRule(), Mock(), XmlAttr('Value'))
        node = Mock(node_globals=InheritedDict(node_globals))

        rule.apply(node=node, expr_body=expr_body, modifier=modifier, attr=xml_attr)

        assert call(node, xml_attr.name, expected_value) == modifier.call_args

    @staticmethod
    @mark.parametrize('value, new_value', [
        (None, True),
        (None, False),
        (False, True),
        (True, False)
    ])
    def test_binds_property_to_expression(value, new_value):
        """apply() should bind property to expression"""
        rule = CheckBoxTwoWaysRule()
        view_model = CheckViewModel(value)
        node = Mock(instance=CheckBoxStub(), node_globals=InheritedDict({'vm': view_model}))

        rule.apply(node=node, expr_body='vm.value', modifier=prop_modifier, attr=XmlAttr('Value'))
        view_model.value = new_value

        assert new_value == node.instance.Value

    @staticmethod
    @mark.parametrize('value, new_value', [
        (False, True),
        (True, False)
    ])
    def test_binds_expression_to_property(value, new_value):
        """apply() should update expression target on EVT_CHECK event"""
        rule = CheckBoxTwoWaysRule()
        view_model = CheckViewModel(value)
        node = Mock(instance=CheckBoxStub(), node_globals=InheritedDict({'vm': view_model}))

        rule.apply(node=node, expr_body='vm.value', attr=XmlAttr('Value'), modifier=prop_modifier)
        node.instance.SetValue(new_value)

        assert new_value == view_model.value

    @staticmethod
    def test_adds_binding_to_node():
        """apply() should add binding to node"""
        rule = TextTwoWaysRule()
        node = Mock(node_globals=InheritedDict({'val': 'value'}))

        rule.apply(node=node, expr_body='val', modifier=Mock(), attr=XmlAttr('Value', 'mod'))
        actual_binding = node.add_binding.call_args[0][0]

        assert node.add_binding.called
        assert isinstance(actual_binding, TwoWaysBinding)
