'''Contains core nodes for wxviews'''

from wx import Sizer # pylint: disable=E0611
from pyviews.core import XmlNode, Node, InstanceNode, InheritedDict
from wxviews.core import WxNode

class SizerNode(InstanceNode, WxNode):
    '''Wrapper under sizer'''
    def __init__(self, instance: Sizer, xml_node: XmlNode,
                 node_globals: InheritedDict = None, parent=None, sizer=None):
        super().__init__(instance, xml_node, node_globals=node_globals)
        self._parent = parent
        self._parent_sizer = sizer
        self._sizer_args: dict = {}

    @property
    def sizer_args(self) -> dict:
        return self._sizer_args

    @sizer_args.setter
    def sizer_args(self, value):
        self._sizer_args = value

    def destroy(self):
        super().destroy()
        if self._parent_sizer is None and self._parent is not None:
            self._parent.SetSizer(None, True)

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
