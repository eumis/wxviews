'''wxviews applictaion entry point'''

from os.path import abspath
from pyviews.core import ioc
from pyviews.rendering.core import apply_attributes, render_children
from pyviews.rendering.binding import BindingFactory, add_default_rules
from pyviews.rendering.dependencies import register_defaults
from pyviews.rendering.views import render_view
from wxviews.rendering import convert_to_node
from wxviews.node import AppNode, FrameNode, ControlNode
from wxviews.sizers import SizerNode

def register_dependencies():
    '''Registers all dependencies needed for application'''
    register_defaults()
    ioc.register_single('views_folder', abspath('views'))
    ioc.register_single('view_ext', '.xml')
    ioc.register_func('convert_to_node', convert_to_node)
    ioc.register_func('set_attr', setattr)
    _register_binding_factory()
    _register_rendering_steps()

def _register_binding_factory():
    factory = BindingFactory()
    add_default_rules(factory)
    ioc.register_single('binding_factory', factory)

def _register_rendering_steps():
    ioc.register_single('rendering_steps', [apply_attributes, render_children], ControlNode)
    ioc.register_single('rendering_steps', [apply_attributes, render_children,
                                            lambda node: node.control.Show()], FrameNode)
    ioc.register_single('rendering_steps', [apply_attributes, render_children], AppNode)
    ioc.register_single('rendering_steps', [apply_attributes, render_children], SizerNode)

def launch(root_view=None):
    '''Runs application. Widgets are created from passed xml_files'''
    root_view = 'root' if root_view is None else root_view
    root = render_view(root_view)
    root.control.MainLoop()
