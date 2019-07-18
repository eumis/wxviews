"""wxviews application entry point"""

from os.path import abspath

from injectool import add_singleton, add_resolve_function, SingletonResolver, add_resolver
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
    add_singleton('views_folder', abspath('views'))
    add_singleton('view_ext', 'xml')
    add_singleton(create_node, create_wx_node)
    add_singleton(render, render_node)
    add_resolve_function(Expression, lambda p, c: CompiledExpression(c))
    add_singleton(Binder, setup_binder())
    add_singleton('namespaces', {'': 'wx', 'init': 'init'})

    add_resolver(RenderingPipeline, get_pipeline_resolver())


def setup_binder() -> Binder:
    """Adds all needed rules to binder"""
    binder = Binder()
    binder.add_rule('once', OnceRule())
    binder.add_rule('oneway', OnewayRule())
    binder.add_rule('twoways', TextTwoWaysRule())
    binder.add_rule('twoways', CheckBoxTwoWaysRule())
    return binder


def get_pipeline_resolver() -> SingletonResolver:
    resolver = SingletonResolver(get_wx_pipeline())
    resolver.add_value(RenderingPipeline(steps=[run_code]), Code)
    resolver.add_value(get_app_pipeline(), App)
    resolver.add_value(get_frame_pipeline(), Frame)
    resolver.add_value(get_container_pipeline(), Container)
    resolver.add_value(get_view_pipeline(), View)
    resolver.add_value(get_for_pipeline(), For)
    resolver.add_value(get_if_pipeline(), If)
    resolver.add_value(get_sizer_pipeline(), SizerNode)
    resolver.add_value(get_growable_row_pipeline(), GrowableRow)
    resolver.add_value(get_growable_col_pipeline(), GrowableCol)
    resolver.add_value(get_menu_bar_pipeline(), MenuBar)
    resolver.add_value(get_menu_pipeline(), Menu)
    resolver.add_value(get_menu_item_pipeline(), MenuItem)
    resolver.add_value(get_style_pipeline(), Style)
    resolver.add_value(get_styles_view_pipeline(), StylesView)
    return resolver


def launch(root_view=None, **render_args):
    """Runs application. Widgets are created from passed xml_files"""
    root_view = 'root' if root_view is None else root_view
    root = render_view(root_view, **render_args)
    root.instance.MainLoop()
