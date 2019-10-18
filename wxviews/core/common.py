from typing import Any

from pyviews.core import InheritedDict
from pyviews.rendering.common import RenderingContext
from wx import Sizer


class WxRenderingContext(RenderingContext):
    """wxviews rendering context"""

    @property
    def parent(self) -> Any:
        """parent control"""
        return self.get('parent', None)

    @parent.setter
    def parent(self, value: Any):
        self['parent'] = value

    @property
    def sizer(self) -> Sizer:
        """Current sizer"""
        return self.get('sizer', None)

    @sizer.setter
    def sizer(self, value: Sizer):
        self['sizer'] = value

    @property
    def node_styles(self) -> InheritedDict:
        return self.get('node_styles', None)

    @node_styles.setter
    def node_styles(self, value: InheritedDict):
        self['node_styles'] = value
