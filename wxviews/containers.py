"""Contains methods for node setups creation"""
from functools import partial

from pyviews.containers import render_container_children, render_view_content, \
    rerender_on_view_change, render_for_items, rerender_on_items_change, render_if, \
    rerender_on_condition_change
from pyviews.core import Observable
from pyviews.rendering import RenderingPipeline

from wxviews.core import WxRenderingContext, apply_attributes


def layout_parent_on_change(changed_property: str, container: Observable,
                            context: WxRenderingContext):
    """Call parent.Layout() on property change"""
    if context.parent:
        container.observe(changed_property, lambda _, __: context.parent.Layout())


def get_container_pipeline() -> RenderingPipeline:
    """Returns setup for container"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        render_container_children
    ], name='container pipeline')


def get_view_pipeline() -> RenderingPipeline:
    """Returns setup for container"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        render_view_content,
        rerender_on_view_change,
        partial(layout_parent_on_change, 'name')
    ], name='view pipeline')


def get_for_pipeline() -> RenderingPipeline:
    """Returns setup for For node"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        render_for_items,
        rerender_on_items_change,
        partial(layout_parent_on_change, 'items')
    ], name='for pipeline')


def get_if_pipeline() -> RenderingPipeline:
    """Returns setup for For node"""
    return RenderingPipeline(pipes=[
        apply_attributes,
        render_if,
        rerender_on_condition_change,
        partial(layout_parent_on_change, 'condition')
    ], name='if pipeline')
