'''Pipeline setup'''

from .common import instance_node_setter, apply_attributes, add_to_sizer
from .containers import  get_container_pipeline, get_view_pipeline
from .containers import  get_for_pipeline, get_if_pipeline
from .menu import get_menu_pipeline, get_menu_bar_pipeline, get_menu_item_pipeline
from .sizers import get_sizer_pipeline, get_growable_col_pipeline, get_growable_row_pipeline
from .wx import get_wx_pipeline, get_app_pipeline, get_frame_pipeline
