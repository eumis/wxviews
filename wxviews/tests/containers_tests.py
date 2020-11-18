from unittest.mock import Mock

from pytest import mark
from pyviews.containers import View, For, If

from wxviews.containers import layout_parent_on_change
from wxviews.core import WxRenderingContext


@mark.parametrize('container, prop', [
    (View(Mock()), 'name'),
    (For(Mock()), 'items'),
    (If(Mock()), 'condition')
])
def test_layout_parent_on_change(container, prop):
    """should call parent.Layout() on property change"""
    parent = Mock()
    context = WxRenderingContext({'parent': parent})

    layout_parent_on_change(prop, container, context)
    setattr(container, prop, 'new value')

    assert parent.Layout.called
