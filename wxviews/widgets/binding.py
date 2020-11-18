"""Binding based on events"""

from functools import partial
from typing import Callable, Any, Type, cast

from injectool import inject
from pyviews.binding import ExpressionBinding, TwoWaysBinding, BindingContext, \
    get_expression_callback, Binder
from pyviews.core import Binding, BindingCallback
from pyviews.expression import Expression
from wx import Event, CommandEvent, EVT_TEXT, EVT_CHECKBOX
from wx import EvtHandler, TextEntry, CheckBox


class EventBinding(Binding):
    """Binds target to wx event"""

    def __init__(self,
                 callback: BindingCallback,
                 evt_handler: EvtHandler,
                 event: Event,
                 get_value: Callable[[CommandEvent], Any] = None):
        super().__init__()
        self._callback = callback
        self._evt_handler = evt_handler
        self._event = event
        self._bound = False
        self._get_value = get_value

    def bind(self):
        self.destroy()
        self._evt_handler.Bind(self._event, self._update_target)
        self._bound = True

    def _update_target(self, evt: CommandEvent):
        value = self._get_value(evt) if self._get_value else evt.GetString()
        self._callback(value)

    def destroy(self):
        if self._bound:
            self._evt_handler.Unbind(self._event, handler=self._update_target)
            self._bound = False


@inject(binder=Binder)
def use_events_binding(binder: Binder = None):
    """Adds twoways binding rules"""
    binder.add_rule('twoways', bind_text_and_expression,
                    lambda ctx: check_control_and_property(cast(Type[EvtHandler], TextEntry), ctx))
    binder.add_rule('twoways', bind_check_and_expression,
                    lambda ctx: check_control_and_property(CheckBox, ctx))


def bind_text_and_expression(context: BindingContext) -> TwoWaysBinding:
    """Binds expression and text entry by EVT_TEXT event"""
    property_expression = Expression(context.expression_body)

    value_callback = partial(context.setter, context.node, context.xml_attr.name)
    expression_binding = ExpressionBinding(value_callback, property_expression,
                                           context.node.node_globals)

    expression_callback = get_expression_callback(property_expression, context.node.node_globals)
    value_binding = EventBinding(expression_callback, context.node.instance, EVT_TEXT)

    two_ways_binding = TwoWaysBinding(expression_binding, value_binding)
    two_ways_binding.bind()
    return two_ways_binding


def bind_check_and_expression(context: BindingContext) -> TwoWaysBinding:
    """Binds expression and text entry by EVT_TEXT event"""
    property_expression = Expression(context.expression_body)

    value_callback = partial(context.setter, context.node, context.xml_attr.name)
    expression_binding = ExpressionBinding(value_callback, property_expression,
                                           context.node.node_globals)

    expression_callback = get_expression_callback(property_expression, context.node.node_globals)
    value_binding = EventBinding(expression_callback, context.node.instance,
                                 EVT_CHECKBOX, lambda evt: evt.IsChecked())

    two_ways_binding = TwoWaysBinding(expression_binding, value_binding)
    two_ways_binding.bind()
    return two_ways_binding


def check_control_and_property(control_type: Type[EvtHandler], context: BindingContext) -> bool:
    """
    Returns True if passed control type equals xml attribute type
    and xml attribute name equals 'Value
    '"""
    try:
        return context.node is not None and isinstance(context.node.instance, control_type) \
               and context.xml_attr is not None and context.xml_attr.name == 'Value'
    except AttributeError:
        return False
