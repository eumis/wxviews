"""wxviews application entry point"""

from os.path import abspath
from typing import cast

from injectool import add_singleton, SingletonResolver, add_resolver
from pyviews.binding import Binder, run_once, bind_setter_to_expression
from pyviews.code import run_code
from pyviews.rendering import RenderingPipeline
from pyviews.rendering.views import render_view

from wxviews.containers import get_if_pipeline, get_for_pipeline
from wxviews.containers import get_view_pipeline, get_container_pipeline
from wxviews.core import WxRenderingContext
from wxviews.menus import get_menu_item_pipeline, get_menu_pipeline, get_menu_bar_pipeline
from wxviews.sizers import get_growable_col_pipeline, get_growable_row_pipeline, get_sizer_pipeline
from wxviews.styles import get_styles_view_pipeline, get_style_pipeline
from wxviews.widgets import get_frame_pipeline, get_app_pipeline, get_wx_pipeline, \
    WxNode, add_events_rules


def register_dependencies():
    """Registers all dependencies needed for application"""
    add_singleton('views_folder', abspath('views'))
    add_singleton('view_ext', 'xml')
    add_singleton(Binder, setup_binder())
    add_resolver(RenderingPipeline, get_pipeline_resolver())


def setup_binder() -> Binder:
    """Adds all needed rules to binder"""
    binder = Binder()
    binder.add_rule('once', run_once)
    binder.add_rule('oneway', bind_setter_to_expression)
    add_events_rules(binder)
    return binder


def get_pipeline_resolver() -> SingletonResolver:
    """Returns resolver for RenderingPipeline"""
    resolver = SingletonResolver()

    resolver.set_value(get_wx_pipeline(), 'wx')
    resolver.set_value(get_app_pipeline(), 'wx.App')
    resolver.set_value(get_frame_pipeline(), 'wx.Frame')

    resolver.set_value(get_container_pipeline(), 'wxviews.Container')
    resolver.set_value(get_view_pipeline(), 'wxviews.View')
    resolver.set_value(get_for_pipeline(), 'wxviews.For')
    resolver.set_value(get_if_pipeline(), 'wxviews.If')

    resolver.set_value(get_sizer_pipeline(), 'wx.GridSizer')
    resolver.set_value(get_sizer_pipeline(), 'wx.FlexGridSizer')
    resolver.set_value(get_sizer_pipeline(), 'wx.GridBagSizer')
    resolver.set_value(get_sizer_pipeline(), 'wx.BoxSizer')
    resolver.set_value(get_sizer_pipeline(), 'wx.StaticBoxSizer')
    resolver.set_value(get_growable_row_pipeline(), 'wxviews.GrowableRow')
    resolver.set_value(get_growable_col_pipeline(), 'wxviews.GrowableCol')

    resolver.set_value(get_menu_bar_pipeline(), 'wx.MenuBar')
    resolver.set_value(get_menu_pipeline(), 'wx.Menu')
    resolver.set_value(get_menu_item_pipeline(), 'wx.MenuItem')

    resolver.set_value(get_style_pipeline(), 'wxviews.Style')
    resolver.set_value(get_styles_view_pipeline(), 'wxviews.StylesView')
    resolver.set_value(RenderingPipeline(pipes=[run_code]), 'wxviews.Code')

    return resolver


def launch(context: WxRenderingContext, root_view=None):
    """Runs application. Widgets are created from passed xml_files"""
    root_view = 'root' if root_view is None else root_view
    root = cast(WxNode, render_view(root_view, context))
    root.instance.MainLoop()
