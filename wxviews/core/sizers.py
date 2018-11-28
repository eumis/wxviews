'''Contains core nodes for wxviews'''

from wx import Sizer # pylint: disable=E0611
from pyviews import Node, InstanceNode, InheritedDict
from pyviews.core.xml import XmlNode

class SizerNode(InstanceNode):
    '''Wrapper under sizer'''
    def __init__(self, instance: Sizer, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(instance, xml_node, node_globals=node_globals)

    def destroy(self):
        super().destroy()
        self.instance.Destroy()

class GrowableRow(Node):
    '''Represents FlexGridSizer.AddGrowableRow method'''
    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(xml_node, node_globals=node_globals)
        self.idx = None
        self.proportion = 0

class GrowableCol(Node):
    '''Represents FlexGridSizer.AddGrowableRow method'''
    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(xml_node, node_globals=node_globals)
        self.idx = None
        self.proportion = 0
