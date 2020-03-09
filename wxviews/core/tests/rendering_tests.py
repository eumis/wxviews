from unittest.mock import Mock

from pytest import fixture, mark

from wxviews.core import WxRenderingContext


@fixture
def rendering_context_fixture(request):
    request.cls.context = WxRenderingContext()


@mark.usefixtures('rendering_context_fixture')
class WxRenderingContextTests:
    """RenderingContext tests"""

    def test_parent(self):
        """parent property should use key 'parent'"""
        value = Mock()
        init_value = self.context.parent

        self.context.parent = value

        assert init_value is None
        assert self.context.parent == value
        assert self.context['parent'] == value

    def test_sizer(self):
        """sizer property should use key 'sizer'"""
        value = Mock()
        init_value = self.context.sizer

        self.context.sizer = value

        assert init_value is None
        assert self.context.sizer == value
        assert self.context['sizer'] == value

    def test_node_styles(self):
        """node_styles property should use key 'node_styles'"""
        value = Mock()
        init_value = self.context.node_styles

        self.context.node_styles = value

        assert init_value is None
        assert self.context.node_styles == value
        assert self.context['node_styles'] == value
