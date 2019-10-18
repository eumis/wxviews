"""Binding based on events"""

from typing import Callable, Any

from injectool import resolve
from wx import EvtHandler, TextEntry, CheckBox
from wx import Event, CommandEvent, EVT_TEXT, EVT_CHECKBOX
from pyviews.core import Expression
from pyviews.core import Binding, BindingTarget
from pyviews.binding import ExpressionBinding, TwoWaysBinding, BindingRule, BindingContext
from pyviews.binding import get_expression_target, PropertyTarget
from pyviews.compilation import parse_expression, is_expression


class EventBinding(Binding):
    """Binds target to wx event"""

    def __init__(self,
                 target: BindingTarget,
                 evt_handler: EvtHandler,
                 event: Event,
                 get_value: Callable[[CommandEvent], Any] = None):
        super().__init__()
        self._target = target
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
        self._target.on_change(value)

    def destroy(self):
        if self._bound:
            self._evt_handler.Unbind(self._event, handler=self._update_target)
            self._bound = False


class TextTwoWaysRule(BindingRule):
    """wx.TextEntry.Value two ways binding"""

    def suitable(self, context: BindingContext) -> bool:
        return context.node is not None and isinstance(context.node.instance, TextEntry) \
               and context.xml_attr is not None and context.xml_attr.name == 'Value'

    def apply(self, context: BindingContext) -> Binding:
        expr_body = parse_expression(context.expression_body)[1] \
            if is_expression(context.expression_body) \
            else context.expression_body
        expression_ = resolve(Expression, expr_body)
        value_target = PropertyTarget(context.node, context.xml_attr.name, context.modifier)
        expression_binding = ExpressionBinding(value_target, expression_, context.node.node_globals)

        expression_target = get_expression_target(expression_, context.node.node_globals)
        value_binding = EventBinding(expression_target, context.node.instance, EVT_TEXT)

        two_ways_binding = TwoWaysBinding(expression_binding, value_binding)
        two_ways_binding.bind()
        return two_ways_binding


class CheckBoxTwoWaysRule(BindingRule):
    """wx.CheckBox.Value two ways binding"""

    def suitable(self, context: BindingContext) -> bool:
        return context.node is not None and isinstance(context.node.instance, CheckBox) \
               and context.xml_attr is not None and context.xml_attr.name == 'Value'

    def apply(self, context: BindingContext):
        expr_body = parse_expression(context.expression_body)[1] \
            if is_expression(context.expression_body) \
            else context.expression_body
        expression_ = resolve(Expression, expr_body)
        value_target = PropertyTarget(context.node, context.xml_attr.name, context.modifier)
        expression_binding = ExpressionBinding(value_target, expression_, context.node.node_globals)

        expression_target = get_expression_target(expression_, context.node.node_globals)
        value_binding = EventBinding(expression_target, context.node.instance,
                                     EVT_CHECKBOX, lambda evt: evt.IsChecked())

        two_ways_binding = TwoWaysBinding(expression_binding, value_binding)
        two_ways_binding.bind()
        return two_ways_binding
