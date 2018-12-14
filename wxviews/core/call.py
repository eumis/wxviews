'''Contains core nodes for wxviews'''

from pyviews import Node, InheritedDict
from pyviews.core.xml import XmlNode

class Call(Node):
    '''Represents FlexGridSizer.AddGrowableRow method'''
    def __init__(self, xml_node: XmlNode, node_globals: InheritedDict = None):
        super().__init__(xml_node, node_globals=node_globals)
        self.method = None
        self._args = []
        self._kwargs = {}

    def add_arg(self, value):
        '''Adds parameter'''
        self._args.append(value)

    def add_kwarg(self, key, value):
        '''Adds parameter with default'''
        self._kwargs[key] = value

    def get_args(self) -> tuple:
        '''Return tuple(args, kwargs)'''
        return (self._args, self._kwargs)
