"""Sandbox view models"""

from typing import List

from pyviews.core.binding import BindableEntity


class SandboxViews(BindableEntity):
    def __init__(self, views: List[str]):
        super().__init__()
        self.all = views
        self.current = views[0]


class TwoWaysViewModel(BindableEntity):
    def __init__(self):
        super().__init__()
        self.text_value = ''
        self.bool_value = False
