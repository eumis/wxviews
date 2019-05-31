"""wxviews application entry point"""

from os.path import abspath

from injectool import register_single, register_func
from pyviews.binding import Binder, OnceRule, OnewayRule
from pyviews.code import run_code, Code
from pyviews.compilation import CompiledExpression
from pyviews.core import Expression, render, create_node
from pyviews.rendering import render_node, RenderingPipeline, render_view
from wx import Frame, App, MenuBar, Menu, MenuItem
from wxviews.binding import TextTwoWaysRule, CheckBoxTwoWaysRule
from wxviews.containers import get_if_pipeline, get_for_pipeline, get_view_pipeline, get_container_pipeline
from wxviews.containers import Container, View, For, If
from wxviews.menus import get_menu_item_pipeline, get_menu_pipeline, get_menu_bar_pipeline
from wxviews.rendering import create_node as create_wx_node
from wxviews.sizers import get_growable_col_pipeline, get_growable_row_pipeline, get_sizer_pipeline
from wxviews.sizers import GrowableCol, GrowableRow, SizerNode
from wxviews.styles import get_styles_view_pipeline, StylesView, get_style_pipeline, Style
from wxviews.widgets import get_frame_pipeline, get_app_pipeline, get_wx_pipeline


def register_dependencies():
    """Registers all dependencies needed for application"""
    register_single('views_folder', abspath('views'))
    register_single('view_ext', 'xml')
    register_func(create_node, create_wx_node)
    register_func(render, render_node)
    register_func(Expression, CompiledExpression)
    register_single(Binder, setup_binder())
    register_single('namespaces', {'': 'wx', 'init': 'init'})

    register_single(RenderingPipeline, RenderingPipeline(steps=[run_code]), Code)
    register_single(RenderingPipeline, get_wx_pipeline())
    register_single(RenderingPipeline, get_app_pipeline(), App)
    register_single(RenderingPipeline, get_frame_pipeline(), Frame)
    register_single(RenderingPipeline, get_container_pipeline(), Container)
    register_single(RenderingPipeline, get_view_pipeline(), View)
    register_single(RenderingPipeline, get_for_pipeline(), For)
    register_single(RenderingPipeline, get_if_pipeline(), If)
    register_single(RenderingPipeline, get_sizer_pipeline(), SizerNode)
    register_single(RenderingPipeline, get_growable_row_pipeline(), GrowableRow)
    register_single(RenderingPipeline, get_growable_col_pipeline(), GrowableCol)
    register_single(RenderingPipeline, get_menu_bar_pipeline(), MenuBar)
    register_single(RenderingPipeline, get_menu_pipeline(), Menu)
    register_single(RenderingPipeline, get_menu_item_pipeline(), MenuItem)
    register_single(RenderingPipeline, get_style_pipeline(), Style)
    register_single(RenderingPipeline, get_styles_view_pipeline(), StylesView)


def setup_binder() -> Binder:
    """Adds all needed rules to binder"""
    binder = Binder()
    binder.add_rule('once', OnceRule())
    binder.add_rule('oneway', OnewayRule())
    binder.add_rule('twoways', TextTwoWaysRule())
    binder.add_rule('twoways', CheckBoxTwoWaysRule())
    return binder


def launch(root_view=None, **render_args):
    """Runs application. Widgets are created from passed xml_files"""
    root_view = 'root' if root_view is None else root_view
    root = render_view(root_view, **render_args)
    root.instance.MainLoop()
