"""wxviews application entry point"""

from typing import cast

from injectool import add_singleton
from pyviews.binding import use_binding
from pyviews.code import run_code
from pyviews.presenter import get_presenter_pipeline
from pyviews.rendering import RenderingPipeline, use_rendering, get_child_context
from pyviews.rendering.pipeline import use_pipeline
from pyviews.rendering.views import render_view

from wxviews.containers import get_if_pipeline, get_for_pipeline
from wxviews.containers import get_view_pipeline, get_container_pipeline
from wxviews.core import WxRenderingContext
from wxviews.core.rendering import get_wx_child_context
from wxviews.menus import get_menu_item_pipeline, get_menu_pipeline, get_menu_bar_pipeline
from wxviews.sizers import get_growable_col_pipeline, get_growable_row_pipeline, get_sizer_pipeline
from wxviews.styles import get_styles_view_pipeline, get_style_pipeline
from wxviews.widgets import get_frame_pipeline, get_app_pipeline, get_wx_pipeline, WxNode
from wxviews.widgets.binding import use_events_binding


def register_dependencies():
    """Registers all dependencies needed for application"""
    use_rendering()
    use_binding()
    use_events_binding()
    use_wx_pipelines()


def use_wx_pipelines():
    """Returns resolver for RenderingPipeline"""
    add_singleton(get_child_context, get_wx_child_context)

    use_pipeline(get_wx_pipeline(), 'wx')
    use_pipeline(get_app_pipeline(), 'wx.App')
    use_pipeline(get_frame_pipeline(), 'wx.Frame')

    use_pipeline(get_container_pipeline(), 'wxviews.Container')
    use_pipeline(get_view_pipeline(), 'wxviews.View')
    use_pipeline(get_for_pipeline(), 'wxviews.For')
    use_pipeline(get_if_pipeline(), 'wxviews.If')

    use_pipeline(get_sizer_pipeline(), 'wx.GridSizer')
    use_pipeline(get_sizer_pipeline(), 'wx.FlexGridSizer')
    use_pipeline(get_sizer_pipeline(), 'wx.GridBagSizer')
    use_pipeline(get_sizer_pipeline(), 'wx.BoxSizer')
    use_pipeline(get_sizer_pipeline(), 'wx.StaticBoxSizer')
    use_pipeline(get_growable_row_pipeline(), 'wxviews.GrowableRow')
    use_pipeline(get_growable_col_pipeline(), 'wxviews.GrowableCol')

    use_pipeline(get_menu_bar_pipeline(), 'wx.MenuBar')
    use_pipeline(get_menu_pipeline(), 'wx.Menu')
    use_pipeline(get_menu_item_pipeline(), 'wx.MenuItem')

    use_pipeline(get_style_pipeline(), 'wxviews.Style')
    use_pipeline(get_styles_view_pipeline(), 'wxviews.StylesView')
    use_pipeline(RenderingPipeline(pipes=[run_code]), 'wxviews.Code')

    use_pipeline(get_presenter_pipeline(), 'wxviews.PresenterNode')


def launch(context: WxRenderingContext, root_view=None):
    """Runs application. Widgets are created from passed xml_files"""
    root_view = 'root' if root_view is None else root_view
    root = cast(WxNode, render_view(root_view, context))
    root.instance.MainLoop()
