'''Contains core nodes for wxviews'''

from typing import Callable
from wx import PyEventBinder, Event # pylint: disable=E0611
from pyviews.core import XmlNode, InstanceNode, InheritedDict

class WxNode(InstanceNode):
    '''Wrapper under wx widget'''
    def __init__(self, instance, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(instance, xml_node, node_globals=node_globals)

    def bind(self, event: PyEventBinder, handler: Callable[[Event], None], **args):
        '''Binds handler to event'''
        self.instance.Bind(event, handler, **args)

    def destroy(self):
        super().destroy()
        self.instance.Destroy()
