"""Package adapts pyviews for using with wxpython"""

from pyviews.setters import import_global, inject_global, set_global, call
from pyviews.code import Code

from wxviews.binding import bind
from wxviews.containers import Container, View, For, If
from wxviews.sizers import GrowableCol, GrowableRow, sizer
from wxviews.widgets.rendering import get_root

__version__ = '0.4.0'
