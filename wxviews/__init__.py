"""Package adapts pyviews for using with wxpython"""

from pyviews.setters import import_global, inject_global, set_global, call
from pyviews.code import Code

from wxviews.containers import Container, View, For, If
from wxviews.sizers import GrowableCol, GrowableRow, set_sizer
from wxviews.widgets import get_root, bind
from wxviews.styles import Style, StylesView, style

__version__ = '0.5.0'
