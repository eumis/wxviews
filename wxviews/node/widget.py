'''Widget node'''

from typing import Callable
from wx import PyEventBinder, Event # pylint: disable=E0611
from pyviews.core import XmlNode, InstanceNode, InheritedDict
from wxviews.core import WxNode

class WidgetNode(InstanceNode, WxNode):
    '''Wrapper under wx widget'''
    def __init__(self, instance, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(instance, xml_node, node_globals=node_globals)
        self._sizer_args: dict = {}

    @property
    def sizer_args(self) -> dict:
        return self._sizer_args

    @sizer_args.setter
    def sizer_args(self, value):
        self._sizer_args = value

    def bind(self, event: PyEventBinder, handler: Callable[[Event], None], **args):
        '''Binds handler to event'''
        self.instance.Bind(event, handler, **args)

    def destroy(self):
        super().destroy()
        self.instance.Destroy()
