"""Package adapts pyviews for using with wxpython"""

from pyviews.rendering.modifiers import import_global, inject_global, set_global, call
from pyviews.code import Code

from wxviews.binding import bind
from wxviews.containers import Container, View, For, If
from wxviews.sizers import GrowableCol, GrowableRow, sizer
from wxviews.styles import Style, StylesView, style
from wxviews.widgets import get_root

__version__ = '0.4.0'
