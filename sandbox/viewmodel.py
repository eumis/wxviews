"""Sandbox view models"""

from typing import List
from pyviews.core import ObservableEntity


class SandboxViews(ObservableEntity):
    def __init__(self, views: List[str]):
        super().__init__()
        self.all = views
        self.current = views[0]


class TwoWaysViewModel(ObservableEntity):
    def __init__(self):
        super().__init__()
        self.text_value = ''
        self.bool_value = False
