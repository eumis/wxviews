import inspect
from typing import Any, Union, List
from unittest.mock import patch

from pyviews.core import Node, InstanceNode
import wx
from wx import Point, DefaultPosition, Size
from wx.lib.agw.customtreectrl import GenericTreeItem
from wx.lib.inspection import InspectionTree, InspectionFrame, InspectionInfoPanel

from wxviews.widgets import WidgetNode, get_root


class ViewInspectionTool:
    """
    The :class:`ViewInspectionTool` is a singleton that manages creating and
    showing an :class:`ViewInspectionFrame`.
    """

    # noinspection PyTypeChecker
    def __init__(self, pos: Point = DefaultPosition, size: Size = Size(850, 700),
                 config=None, crust_locals: dict = None):
        self._frame: ViewInspectionFrame = None
        self._pos: Point = pos
        self._size: Size = size
        self._config = config
        self._crust_locals: dict = crust_locals
        if not hasattr(self, '_app'):
            self._app: WidgetNode = get_root()

    def show(self, select_obj: Any = None):
        """
        Creates the inspection frame if it hasn't been already, and
        raises it if neccessary.

        :param select_obj: Pass a widget or sizer to have that object be
                     preselected in widget tree.
        """
        if not self._frame:
            self._frame = ViewInspectionFrame(parent=self._app.instance.GetTopWindow(),
                                              pos=self._pos,
                                              size=self._size,
                                              config=self._config,
                                              locals=self._crust_locals,
                                              app=self._app.instance,
                                              root=self._app)
        self._frame.SetObj(select_obj if select_obj else self._app)
        self._frame.Show()
        if self._frame.IsIconized():
            self._frame.Iconize(False)
        self._frame.Raise()


class ViewInspectionFrame(InspectionFrame):
    """
    This class is the frame that holds the wxPython inspection tools.
    The toolbar and AUI splitters/floating panes are also managed
    here.  The contents of the tool windows are handled by other
    classes.
    """

    def __init__(self, *args, root=None, **kwargs):
        from wx.lib import inspection
        with patch(f'{inspection.__name__}.{InspectionTree.__name__}', ViewInspectionTree):
            with patch(f'{inspection.__name__}.{InspectionInfoPanel.__name__}', ViewInspectionInfoPanel):
                InspectionFrame.__init__(self, *args, **kwargs)
                self.locals['root'] = root


class ViewInspectionTree(InspectionTree):
    def BuildTree(self, startWidget, includeSizers=False, expandFrame=False):
        """setup root"""
        if isinstance(startWidget, Node):
            self.BuildNodeTree(startWidget)
        else:
            super().BuildTree(startWidget, includeSizers=includeSizers, expandFrame=expandFrame)

    def BuildNodeTree(self, startNode: Node):
        """setup root"""
        if self.GetCount():
            self.DeleteAllItems()
            self.roots = []
            self.built = False

        root = get_root()
        root_item = self.AddRoot(self._get_node_name(startNode))
        self.SetItemData(root_item, root)

        for child in root.children:
            self.add_node(root_item, child)

        # Expand the subtree containing the startWidget, and select it.
        self.built = True
        self.SelectObj(startNode)

    def _get_node_name(self, node: Union[Node, InstanceNode]):
        node_name = node.__class__.__name__
        try:
            return f'{self.GetTextForWidget(node.instance)}[{node_name}]'
        except AttributeError:
            return node_name

    def add_node(self, parent_item: GenericTreeItem, node: Union[Node, InstanceNode]) -> GenericTreeItem:
        text = self._get_node_name(node)
        item = self.AppendItem(parent_item, text)
        self.SetItemData(item, node)

        for child in node.children:
            self.add_node(item, child)

        return item

    def _add_binding(self, parentItem, binding):
        text = binding.__class__.__name__
        item = self.AppendItem(parentItem, text)
        self.SetItemData(item, binding)
        self.SetItemTextColour(item, "orange")
        return item


class ViewInspectionInfoPanel(InspectionInfoPanel):
    def UpdateInfo(self, obj):
        """add node formatter"""
        st = []
        if not obj:
            st.append("Item is None or has been destroyed.")

        if isinstance(obj, Node):
            st += self.format_node(obj)
            if hasattr(obj, 'instance'):
                st += self._format_wx_item(obj.instance)
        else:
            st += self._format_wx_item(obj)

        self.SetReadOnly(False)
        self.SetText('\n'.join(st))
        self.SetReadOnly(True)

    def _format_wx_item(self, obj: Any) -> List[str]:
        if isinstance(obj, wx.Window):
            return self.FmtWidget(obj)

        elif isinstance(obj, wx.Sizer):
            return self.FmtSizer(obj)

        elif isinstance(obj, wx.SizerItem):
            return self.FmtSizerItem(obj)

        return []

    def format_node(self, obj: Node) -> List[str]:
        st = [
            "Node:",
            self.Fmt('class', obj.__class__),
            self.Fmt('bases', obj.__class__.__bases__),
            self.Fmt('module', inspect.getmodule(obj))
        ]

        keys = [key for key in dir(obj) if not key.startswith('_')]
        for key in keys:
            st.append(self.Fmt(key, getattr(obj, key)))

        st.append("node_globals:")
        for key, value in obj.node_globals.to_dictionary().items():
            st.append(self.Fmt(key, value))

        return st
