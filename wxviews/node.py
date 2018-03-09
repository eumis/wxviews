'''wx control nodes'''

from wx.core import Control, Frame, Sizer
from pyviews.core.node import Node, NodeArgs
from pyviews.core.xml import XmlNode

class ControlArgs(NodeArgs):
    '''NodeArgs for ControlNode'''
    def __init__(self, xml_node, parent_node=None, parent_control=None):
        super().__init__(xml_node, parent_node)
        self['parent'] = parent_control

    def get_args(self, inst_type=None):
        if issubclass(inst_type, Sizer):
            return NodeArgs.Result([], {})
        if issubclass(inst_type, Node):
            return super().get_args(inst_type)
        return NodeArgs.Result([self['parent']], {})

class ControlNode(Node):
    '''Wrapper under wx control'''
    def __init__(self, control, xml_node: XmlNode, parent_context=None):
        super().__init__(xml_node, parent_context)
        self.control = control
        self.sizer_args = []
        self.sizer_kwargs = {}

    def get_node_args(self, xml_node: XmlNode):
        return ControlArgs(xml_node, self, self.control)

class FrameNode(ControlNode):
    '''Wrapper under wx Frame'''
    pass

class AppNode(ControlNode):
    '''Wrapper under wx App'''
    def get_node_args(self, xml_node: XmlNode):
        return ControlArgs(xml_node, self, None)
