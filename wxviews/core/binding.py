'''Binding rules'''

from wx import TextEntry, Event, EvtHandler, EVT_TEXT # pylint: disable=E0611
from pyviews import Modifier
from pyviews.core.xml import XmlAttr
from pyviews.core.compilation import Expression
from pyviews.core.binding import Binding, ExpressionBinding, TwoWaysBinding
from pyviews.core.binding import BindingTarget, PropertyTarget, FunctionTarget
from pyviews.core.binding import get_expression_target
from pyviews.rendering.expression import parse_expression
from pyviews.rendering.binding import BindingRule
from wxviews.core.node import WxNode

# pylint: disable=W0221

class EventBinding(Binding):
    '''Binds target to wx event'''
    def __init__(self, target: BindingTarget, evt_handler: EvtHandler, event: Event):
        super().__init__()
        self._target = target
        self._evt_handler = evt_handler
        self._event = event
        self._binded = False

    def bind(self):
        self.destroy()
        self._evt_handler.Bind(self._event, self._update_target)
        self._binded = True

    def _update_target(self, evt):
        self._target.on_change(evt.GetString())

    def destroy(self):
        if self._binded:
            self._evt_handler.Unbind(self._event, handler=self._update_target)
            self._binded = False

class TextTwoWaysRule(BindingRule):
    '''Defines two ways binding for TextEntry using '''
    def suitable(self,
                 node: WxNode = None,
                 attr: XmlAttr = None,
                 **args) -> bool:
        return node is not None and isinstance(node.instance, TextEntry)\
               and attr is not None and attr.name == 'Value'

    def apply(self,
              node: WxNode = None,
              expr_body: str = None,
              modifier: Modifier = None,
              attr: XmlAttr = None,
              **args):
        '''Applies binding'''
        expression = Expression(parse_expression(expr_body)[1])
        value_target = FunctionTarget(lambda value, n=node: self._set_control_value(n, value))\
                       if attr.namespace is None else\
                       PropertyTarget(node, attr.name, modifier)
        expression_binding = ExpressionBinding(value_target, expression, node.node_globals)

        expression_target = get_expression_target(expression, node.node_globals)
        value_binding = EventBinding(expression_target, node.instance, EVT_TEXT)

        two_ways_binding = TwoWaysBinding(expression_binding, value_binding)
        two_ways_binding.bind()
        node.add_binding(two_ways_binding)

    def _set_control_value(self, node: WxNode, value: str):
        node.instance.ChangeValue(value)
