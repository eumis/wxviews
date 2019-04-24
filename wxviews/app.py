"""wxviews application entry point"""

from os.path import abspath
from wx import Frame, App, MenuBar, Menu, MenuItem
from pyviews.core import ioc, Binder
from pyviews.compilation import CompiledExpression
from pyviews.binding import add_one_way_rules
from pyviews.rendering import render_node, render_view, RenderingPipeline
from pyviews.code import Code, run_code
from wxviews.binding import add_two_ways_rules
from wxviews.containers import get_if_pipeline, get_for_pipeline, get_view_pipeline, get_container_pipeline
from wxviews.containers import Container, View, For, If
from wxviews.menus import get_menu_item_pipeline, get_menu_pipeline, get_menu_bar_pipeline
from wxviews.sizers import get_growable_col_pipeline, get_growable_row_pipeline, get_sizer_pipeline
from wxviews.sizers import GrowableCol, GrowableRow, SizerNode
from wxviews.styles import get_styles_view_pipeline, StylesView, get_style_pipeline, Style
from wxviews.rendering import create_node
from wxviews.widgets import get_frame_pipeline, get_app_pipeline, get_wx_pipeline


def register_dependencies():
    """Registers all dependencies needed for application"""
    ioc.register_single('views_folder', abspath('views'))
    ioc.register_single('view_ext', 'xml')
    ioc.register_func('create_node', create_node)
    ioc.register_func('render', render_node)
    ioc.register_func('expression', CompiledExpression)
    ioc.register_single('binder', setup_binder())
    ioc.register_single('namespaces', {'': 'wx', 'init': 'init'})

    ioc.register_single('pipeline', RenderingPipeline(steps=[run_code]), Code)
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
    ioc.register_single('pipeline', get_style_pipeline(), Style)
    ioc.register_single('pipeline', get_styles_view_pipeline(), StylesView)


def setup_binder() -> Binder:
    """Adds all needed rules to binder"""
    binder = Binder()
    add_one_way_rules(binder)
    add_two_ways_rules(binder)
    return binder


def launch(root_view=None, **render_args):
    """Runs application. Widgets are created from passed xml_files"""
    root_view = 'root' if root_view is None else root_view
    root = render_view(root_view, **render_args)
    root.instance.MainLoop()
