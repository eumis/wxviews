from unittest.mock import Mock, call

from pytest import fixture, mark
from pyviews.binding.binder import BindingContext
from pyviews.binding.twoways import TwoWaysBinding
from pyviews.core.binding import BindableEntity
from pyviews.core.rendering import Node, NodeGlobals
from pyviews.core.xml import XmlAttr
from pyviews.pipes import call_set_attr
from wx import EVT_CHECKBOX, EVT_TEXT, CheckBox, TextCtrl

from wxviews.widgets.binding import (EventBinding, bind_check_and_expression, bind_text_and_expression,
                                     check_control_and_property)
from wxviews.widgets.rendering import WxNode


class EventHandlerStub:

    def __init__(self, event):
        self._handler = None
        self._event = event

    def Bind(self, event, handler):
        if event == self._event:
            self._handler = handler

    def Unbind(self, event, handler = None):
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


def prop_setter(node, prop, value):
    setattr(node.instance, prop, value)


class EventBindingTests:
    """EventBinding class tests"""

    @staticmethod
    def test_binds():
        """bind() bind callback to event and use event.GetString() for value"""
        callback, value = (Mock(), 'some value')
        evt_handler, event = (TextEntryStub(), EVT_TEXT)
        binding = EventBinding(callback, evt_handler, event)

        binding.bind()
        evt_handler.ChangeValue(value)

        assert call(value) == callback.call_args

    @staticmethod
    def test_binds_with_get_value():
        """bind() bind callback to event and use passed get_value for value"""
        callback, value = (Mock(), True)
        evt_handler, event = (CheckBoxStub(), EVT_CHECKBOX)
        binding = EventBinding(callback, evt_handler, event, lambda evt: evt.IsChecked())

        binding.bind()
        evt_handler.SetValue(value)

        assert call(value) == callback.call_args

    @staticmethod
    def test_destroy():
        """should unbind callback from event"""
        target, value = (Mock(), 'some value')
        evt_handler, event = (TextEntryStub(), EVT_TEXT)
        binding = EventBinding(target, evt_handler, event)
        binding.bind()

        binding.destroy()

        evt_handler.ChangeValue(value)
        assert not target.on_change.called


class TextViewModel(BindableEntity):

    def __init__(self, value = None):
        super().__init__()
        self.text_value = value


@fixture
def text_binding_fixture(request):
    text, vm = TextEntryStub(), TextViewModel()
    node = WxNode(text, Mock(), NodeGlobals({'vm': vm}))

    context = BindingContext()
    context.node = node
    context.xml_attr = XmlAttr('Value')
    context.setter = call_set_attr
    context.expression_body = "vm.text_value"

    request.cls.context = context
    request.cls.text = text
    request.cls.vm = vm


@mark.usefixtures('text_binding_fixture')
class BindTextAndExpressionTests:
    """bind_text_and_expression() tests"""

    context: BindingContext
    text: TextEntryStub
    vm: TextViewModel

    def test_returns_binding(self):
        """should return TwoWaysBinding()"""

        binding = bind_text_and_expression(self.context)

        assert isinstance(binding, TwoWaysBinding)

    @mark.parametrize('init_value, new_value', [
        ('one', 'two'),
        ('two', 'two'),
        ('two', 'three')
    ]) # yapf: disable
    def tests_binds_control_value_to_expression(self, init_value, new_value):
        """should bind TextEntry.Value to expression"""
        self.vm.text_value = init_value

        bind_text_and_expression(self.context)
        self.vm.text_value = new_value

        assert self.text.Value == new_value

    @mark.parametrize('init_value, new_value', [
        ('one', 'two'),
        ('two', 'two'),
        ('two', 'three')
    ]) # yapf: disable
    def tests_binds_expression_to_control(self, init_value, new_value):
        """should bind bind view model to control value"""
        self.vm.text_value = init_value

        bind_text_and_expression(self.context)
        self.text.ChangeValue(new_value)

        assert self.vm.text_value == new_value


class CheckViewModel(BindableEntity):

    def __init__(self, value = None):
        super().__init__()
        self.value = value


@fixture
def check_binding_fixture(request):
    checkbox, vm = CheckBoxStub(), CheckViewModel()
    node = WxNode(checkbox, Mock(), NodeGlobals({'vm': vm}))

    context = BindingContext()
    context.node = node
    context.xml_attr = XmlAttr('Value')
    context.setter = call_set_attr
    context.expression_body = "vm.value"

    request.cls.context = context
    request.cls.checkbox = checkbox
    request.cls.vm = vm


@mark.usefixtures('check_binding_fixture')
class BindCheckAndExpressionTests:
    """bind_check_and_expression() tests"""

    context: BindingContext
    checkbox: CheckBoxStub
    vm: CheckViewModel

    def test_returns_binding(self):
        """should return TwoWaysBinding()"""

        binding = bind_check_and_expression(self.context)

        assert isinstance(binding, TwoWaysBinding)

    @mark.parametrize('init_value, new_value', [
        (True, False),
        (False, True)
    ]) # yapf: disable
    def tests_binds_control_value_to_expression(self, init_value, new_value):
        """should bind CheckBox.Value to expression"""
        self.vm.value = init_value

        bind_check_and_expression(self.context)
        self.vm.value = new_value

        assert self.checkbox.Value == new_value

    @mark.parametrize('init_value, new_value', [
        (True, False),
        (False, True)
    ]) # yapf: disable
    def tests_binds_expression_to_control(self, init_value, new_value):
        """should bind bind view model to control value"""
        self.vm.value = init_value

        bind_check_and_expression(self.context)
        self.checkbox.SetValue(new_value)

        assert self.vm.value == new_value


@mark.parametrize('control_type, binding_context, expected', [
    (TextEntryStub,
     {'node': WxNode(TextEntryStub(), Mock()), 'xml_attr': XmlAttr('Value')},
     True),
    (TextEntryStub,
     {'node': WxNode(CheckBoxStub(), Mock()), 'xml_attr': XmlAttr('Value')},
     False),
    (TextEntryStub,
     {'node': WxNode(TextEntryStub(), Mock()), 'xml_attr': XmlAttr('Property')},
     False),
    (CheckBoxStub,
     {'node': WxNode(CheckBoxStub(), Mock()), 'xml_attr': XmlAttr('Value')},
     True),
    (CheckBoxStub,
     {'node': WxNode(TextEntryStub(), Mock()), 'xml_attr': XmlAttr('Value')},
     False),
    (CheckBoxStub,
     {'node': WxNode(CheckBoxStub(), Mock()), 'xml_attr': XmlAttr('Property')},
     False),
    (CheckBoxStub, {}, False),
    (TextEntryStub, {'node': WxNode(TextEntryStub(), Mock())}, False),
    (CheckBoxStub, {'xml_attr': XmlAttr('text')}, False),
    (TextEntryStub, {'node': Node(Mock()), 'xml_attr': XmlAttr('text')}, False)
]) # yapf: disable
def test_check_control_and_property(control_type, binding_context, expected):
    """should return true if control type and value property equal to items from context"""
    actual = check_control_and_property(control_type, BindingContext(**binding_context))

    assert actual == expected
