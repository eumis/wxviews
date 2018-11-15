'''Contains core nodes for wxviews'''

from pyviews import InstanceNode, InheritedDict
from pyviews.core.xml import XmlNode

class WxNode(InstanceNode):
    '''Wrapper under wx widget'''
    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(None, xml_node, node_globals=node_globals)

    def init(self, instance):
        '''Initializes instance with provided args'''
        if self._instance is not None:
            raise 'node is already initialized'
        self._instance = instance

    def destroy(self):
        super().destroy()
        self.instance.Destroy()
