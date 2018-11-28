'''wxviews applictaion entry point'''

# from os.path import abspath
# from pyviews.core import ioc
# from pyviews.rendering.binding import BindingFactory, add_default_rules
# from pyviews.dependencies import register_defaults
# from pyviews.rendering.views import render_view
# from wxviews.node import AppNode, FrameNode, show_frame
# from wxviews.sizers import SizerNode, set_sizer, add_to_sizer
# from wxviews.containers import Container, View, For, If
# from pyviews.dependencies import create_node

# def register_dependencies():
#     '''Registers all dependencies needed for application'''
#     register_defaults()
#     ioc.register_single('views_folder', abspath('views'))
#     ioc.register_single('view_ext', '.xml')
#     ioc.register_single('custom_events', {})
#     ioc.register_func('convert_to_node', convert_to_node)
#     ioc.register_func('set_attr', setattr)
#     _register_binding_factory()
#     _register_rendering_steps()

# def _register_binding_factory():
#     factory = BindingFactory()
#     add_default_rules(factory)
#     ioc.register_single('binding_factory', factory)

# def _register_rendering_steps():
#     ioc.register_single('rendering_steps', [apply_attributes, render_children, add_to_sizer])
#     ioc.register_single('rendering_steps',
#                         [apply_attributes, render_children],
#                         AppNode)
#     ioc.register_single('rendering_steps',
#                         [apply_attributes, render_children, show_frame],
#                         FrameNode)
#     ioc.register_single('rendering_steps',
#                         [apply_attributes, render_children, set_sizer, add_to_sizer],
#                         SizerNode)
#     ioc.register_single('rendering_steps',
#                         [apply_attributes, render_children],
#                         Container)
#     ioc.register_single('rendering_steps',
#                         [apply_attributes, render_children],
#                         If)
#     ioc.register_single('rendering_steps',
#                         [apply_attributes, render_children],
#                         For)
#     ioc.register_single('rendering_steps',
#                         [apply_attributes, render_children],
#                         View)

# def launch(root_view=None):
#     '''Runs application. Widgets are created from passed xml_files'''
#     root_view = 'root' if root_view is None else root_view
#     root = render_view(root_view)
#     root.wx_instance.MainLoop()

from os.path import abspath
from wx import Frame, App # pylint: disable=E0611
from pyviews.core import ioc
from pyviews.rendering.binding import BindingFactory, add_default_rules
from pyviews.rendering.views import render_view
from pyviews.dependencies import register_defaults
from wxviews.core.containers import Container, View, For, If
from wxviews.core.sizers import SizerNode, GrowableCol, GrowableRow
from wxviews.pipeline.instance import get_frame_pipeline, get_wx_pipeline, get_app_pipeline
from wxviews.pipeline.containers import get_container_pipeline, get_view_pipeline
from wxviews.pipeline.containers import get_for_pipeline, get_if_pipeline
from wxviews.pipeline.sizers import get_sizer_pipeline
from wxviews.pipeline.sizers import get_growable_row_pipeline, get_growable_col_pipeline
from wxviews.rendering import create_node

def register_dependencies():
    '''Registers all dependencies needed for application'''
    register_defaults()

    ioc.register_single('views_folder', abspath('views'))
    ioc.register_single('view_ext', 'xml')
    ioc.register_func('create_node', create_node)
    _register_binding_factory()

    ioc.register_single('pipeline', get_wx_pipeline())
    ioc.register_single('pipeline', get_app_pipeline(), App)
    ioc.register_single('pipeline', get_frame_pipeline(), Frame)
    ioc.register_single('pipeline', get_container_pipeline(), Container)
    ioc.register_single('pipeline', get_view_pipeline(), View)
    ioc.register_single('pipeline', get_for_pipeline(), For)
    ioc.register_single('pipeline', get_if_pipeline(), If)
    ioc.register_single('pipeline', get_sizer_pipeline(), SizerNode)
    ioc.register_single('pipeline', get_growable_row_pipeline(), GrowableRow)
    ioc.register_single('pipeline', get_growable_col_pipeline(), GrowableCol)

def _register_binding_factory():
    factory = BindingFactory()
    add_default_rules(factory)
    ioc.register_single('binding_factory', factory)

def launch(root_view=None):
    '''Runs application. Widgets are created from passed xml_files'''
    root_view = 'root' if root_view is None else root_view
    root = render_view(root_view)
    root.instance.MainLoop()
