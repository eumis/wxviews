'''wx control nodes'''

from wx import Control, Frame, Sizer, GridSizer
from wx.core import PyEventBinder
from pyviews.core.node import Node, RenderArgs
from pyviews.core.xml import XmlNode
from pyviews.rendering.core import render_step

class WxRenderArgs(RenderArgs):
    '''RenderArgs for ControlNode'''
    def __init__(self, xml_node, parent_node=None, parent=None):
        super().__init__(xml_node, parent_node)
        self['parent'] = parent
        self['sizer'] = None

    def get_args(self, inst_type):
        if issubclass(inst_type, GridSizer):
            return RenderArgs.Result([0, 0, 0], {})
        if issubclass(inst_type, Sizer):
            return RenderArgs.Result([], {})
        if issubclass(inst_type, Node):
            return super().get_args(inst_type)
        return RenderArgs.Result([self['parent']], {})

class ControlNode(Node):
    '''Wrapper under wx control'''
    def __init__(self, wx_inst, xml_node: XmlNode, parent_context=None):
        super().__init__(xml_node, parent_context)
        self._control = wx_inst
        self.sizer_args = []
        self.sizer_kwargs = {}

    @property
    def wx_instance(self):
        '''wx control that wrapped by node'''
        return self._control

    def bind(self, event: PyEventBinder, command):
        '''Binds control to event'''
        self._control.Bind(event, command)

    def get_render_args(self, xml_node: XmlNode):
        return WxRenderArgs(xml_node, self, self._control)

class FrameNode(ControlNode):
    '''Wrapper under wx Frame'''
    pass

class AppNode(ControlNode):
    '''Wrapper under wx App'''
    def get_render_args(self, xml_node: XmlNode):
        return WxRenderArgs(xml_node, self, None)

@render_step
def show_frame(node: FrameNode):
    '''Calls frame show'''
    node.wx_instance.Show()
