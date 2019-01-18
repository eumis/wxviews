'''wxviews applictaion entry point'''

from os.path import abspath
from wx import Frame, App, MenuBar, Menu, MenuItem # pylint: disable=E0611
from pyviews.core import ioc
from pyviews.rendering.binding import Binder, add_default_rules
from pyviews.rendering.views import render_view
from pyviews.dependencies import register_defaults
from wxviews.core.containers import Container, View, For, If
from wxviews.core.sizers import SizerNode, GrowableCol, GrowableRow
from wxviews.pipeline.wx import get_frame_pipeline, get_wx_pipeline, get_app_pipeline
from wxviews.pipeline.containers import get_container_pipeline, get_view_pipeline
from wxviews.pipeline.containers import get_for_pipeline, get_if_pipeline
from wxviews.pipeline.sizers import get_sizer_pipeline
from wxviews.pipeline.sizers import get_growable_row_pipeline, get_growable_col_pipeline
from wxviews.pipeline.menu import get_menu_bar_pipeline, get_menu_pipeline, get_menu_item_pipeline
from wxviews.rendering import create_node

def register_dependencies():
    '''Registers all dependencies needed for application'''
    register_defaults()

    ioc.register_single('views_folder', abspath('views'))
    ioc.register_single('view_ext', 'xml')
    ioc.register_func('create_node', create_node)
    _register_binder()

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
    ioc.register_single('pipeline', get_menu_bar_pipeline(), MenuBar)
    ioc.register_single('pipeline', get_menu_pipeline(), Menu)
    ioc.register_single('pipeline', get_menu_item_pipeline(), MenuItem)

def _register_binder():
    binder = Binder()
    add_default_rules(binder)
    ioc.register_single('binder', binder)

def launch(root_view=None, **render_args):
    '''Runs application. Widgets are created from passed xml_files'''
    root_view = 'root' if root_view is None else root_view
    root = render_view(root_view, **render_args)
    root.instance.MainLoop()
