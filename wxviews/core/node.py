'''Contains core nodes for wxviews'''

from pyviews import InstanceNode, InheritedDict
from pyviews.core.xml import XmlNode

class WxNode(InstanceNode):
    '''Wrapper under wx widget'''
    def __init__(self, instance, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(instance, xml_node, node_globals=node_globals)

    def destroy(self):
        super().destroy()
        self.instance.Destroy()
