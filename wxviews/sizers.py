'''Sizer wrappers'''

from wx import Control
from pyviews.core.xml import XmlNode
from pyviews.core.node import Node
from pyviews.rendering.core import render_step
from wxviews.node import WxRenderArgs

class SizerNode(Node):
    '''Wrapper under sizer'''
    def __init__(self, wx_inst, xml_node: XmlNode, parent_context=None, parent=None):
        super().__init__(xml_node, parent_context)
        self._parent = parent
        self._sizer = wx_inst
        self.sizer_args = []
        self.sizer_kwargs = {}

    @property
    def wx_instance(self):
        '''wx sizer that wrapped by node'''
        return self._sizer

    def get_render_args(self, xml_node: XmlNode):
        args = WxRenderArgs(xml_node, self, self._parent)
        args['sizer'] = self._sizer
        return args

@render_step('sizer', 'parent')
def set_sizer(node: SizerNode, sizer=None, parent=None):
    '''Use sizer for parent control'''
    if sizer is None:
        parent.SetSizer(node.wx_instance)

@render_step('sizer')
def add_to_sizer(node, sizer=None):
    '''Adds control to sizer'''
    if sizer is not None:
        sizer.Add(node.wx_instance, *node.sizer_args, **node.sizer_kwargs)
