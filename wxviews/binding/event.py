"""Binding based on events"""

from typing import Callable, Any

from injectool import resolve
from wx import EvtHandler, TextEntry, CheckBox
from wx import Event, CommandEvent, EVT_TEXT, EVT_CHECKBOX
from pyviews.core import Modifier, XmlAttr, InstanceNode, Expression
from pyviews.core import Binding, BindingTarget, BindingRule
from pyviews.binding import ExpressionBinding, TwoWaysBinding
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

    @staticmethod
    def suitable(node: InstanceNode = None,
                 attr: XmlAttr = None,
                 **args) -> bool:
        return node is not None and isinstance(node.instance, TextEntry) \
               and attr is not None and attr.name == 'Value'

    @staticmethod
    def apply(node: InstanceNode = None,
              expr_body: str = None,
              modifier: Modifier = None,
              attr: XmlAttr = None,
              **args):
        expr_body = parse_expression(expr_body)[1] if is_expression(expr_body) else expr_body
        expression_ = resolve(Expression, expr_body)
        value_target = PropertyTarget(node, attr.name, modifier)
        expression_binding = ExpressionBinding(value_target, expression_, node.node_globals)

        expression_target = get_expression_target(expression_, node.node_globals)
        value_binding = EventBinding(expression_target, node.instance, EVT_TEXT)

        two_ways_binding = TwoWaysBinding(expression_binding, value_binding)
        two_ways_binding.bind()
        node.add_binding(two_ways_binding)


class CheckBoxTwoWaysRule(BindingRule):
    """wx.CheckBox.Value two ways binding"""

    @staticmethod
    def suitable(node: InstanceNode = None,
                 attr: XmlAttr = None,
                 **args) -> bool:
        return node is not None and isinstance(node.instance, CheckBox) \
               and attr is not None and attr.name == 'Value'

    @staticmethod
    def apply(node: InstanceNode = None,
              expr_body: str = None,
              modifier: Modifier = None,
              attr: XmlAttr = None,
              **args):
        expr_body = parse_expression(expr_body)[1] if is_expression(expr_body) else expr_body
        expression_ = resolve(Expression, expr_body)
        value_target = PropertyTarget(node, attr.name, modifier)
        expression_binding = ExpressionBinding(value_target, expression_, node.node_globals)

        expression_target = get_expression_target(expression_, node.node_globals)
        value_binding = EventBinding(expression_target, node.instance,
                                     EVT_CHECKBOX, lambda evt: evt.IsChecked())

        two_ways_binding = TwoWaysBinding(expression_binding, value_binding)
        two_ways_binding.bind()
        node.add_binding(two_ways_binding)
