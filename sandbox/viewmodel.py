'''Sandbox view models'''

from typing import List
from pyviews import ObservableEntity

class SandboxViews(ObservableEntity):
    def __init__(self, views: List[str]):
        super().__init__()
        self.all = views
        self.current = views[0]
