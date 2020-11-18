"""Package adapts pyviews for using with wxpython"""

from pyviews.setters import import_global, inject_global, set_global, call, call_args
from pyviews.code import Code
from pyviews.containers import Container, View, For, If
from pyviews.presenter import Presenter, PresenterNode, add_reference

from wxviews.sizers import GrowableCol, GrowableRow, set_sizer
from wxviews.widgets import get_root, bind
from wxviews.styles import Style, StylesView, style

__version__ = '0.6.0'
