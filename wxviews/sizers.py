'''Sizer wrappers'''

from pyviews.core.xml import XmlNode
from wxviews.node import ControlNode, ControlArgs

class SizerNode(ControlNode):
    '''Wrapper under sizer'''
    def __init__(self, control, xml_node: XmlNode, parent_context=None, parent=None, parent_node=None): 
        super().__init__(control, xml_node, parent_context)
        self._parent_node = parent_node
        self._parent = parent

    def render_children(self):
        super().render_children()
        for child_node in self._child_nodes:
            self.control.Add(child_node.control, *child_node.sizer_args, **child_node.sizer_kwargs)
        if not isinstance(self._parent_node, SizerNode):
            self._parent_node.control.SetSizer(self.control)

    def get_node_args(self, xml_node: XmlNode):
        return ControlArgs(xml_node, self, self._parent)
