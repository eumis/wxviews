from os import linesep
import inspect
from traceback import format_exc
from typing import Any, Union, List
from unittest.mock import patch

from pyviews.binding import ExpressionBinding, PropertyTarget, FunctionTarget, PropertyExpressionTarget, \
    GlobalValueExpressionTarget, ObservableBinding, TwoWaysBinding
from pyviews.core import Node, InstanceNode
import wx
from wx import Point, DefaultPosition, Size
from wx.lib.agw.customtreectrl import GenericTreeItem
from wx.lib.inspection import InspectionTree, InspectionFrame, InspectionInfoPanel

from wxviews.binding import EventBinding
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
    # noinspection PyPep8Naming
    def BuildTree(self, start_widget, includeSizers=False, expandFrame=False):
        """setup root"""
        if isinstance(start_widget, Node):
            self.build_node_tree(start_widget)
        else:
            super().BuildTree(start_widget, includeSizers=includeSizers, expandFrame=expandFrame)

    def build_node_tree(self, start_node: Node):
        """setup root"""
        if self.GetCount():
            self.DeleteAllItems()
            self.roots = []
            self.built = False

        root = get_root()
        root_item = self.AddRoot(self._get_node_name(root))
        self.SetItemData(root_item, root)
        self.roots = [root_item]

        for child in root.children:
            self.add_node(root_item, child)

        # Expand the subtree containing the startWidget, and select it.
        self.built = True
        self.SelectObj(start_node)

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

    def _add_binding(self, parent_item, binding):
        text = binding.__class__.__name__
        item = self.AppendItem(parent_item, text)
        self.SetItemData(item, binding)
        self.SetItemTextColour(item, "orange")
        return item


class ViewInspectionInfoPanel(InspectionInfoPanel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._evt_names = {}
        evt_names = [x for x in dir(wx) if x.startswith("EVT_")]
        for name in evt_names:
            evt = getattr(wx, name)
            if isinstance(evt, wx.PyEventBinder):
                self._evt_names[evt.typeId] = name

    def UpdateInfo(self, obj):
        """add node formatter"""
        if not obj:
            self._set_text(["Item is None or has been destroyed."])
            return

        try:
            if isinstance(obj, Node):
                st = []
                st += self.format_node(obj)
                if hasattr(obj, 'instance'):
                    st += self._format_wx_item(obj.instance)
                self._set_text(st)
            else:
                super().UpdateInfo(obj)
        except RuntimeError:
            self._set_text(['Failed to show info.', format_exc()])

    def _set_text(self, st):
        self.SetReadOnly(False)
        self.SetText(linesep.join(st))
        self.SetReadOnly(True)

    def _format_wx_item(self, obj: Any) -> List[str]:
        if isinstance(obj, wx.MenuBar):
            return self.format_menu_bar(obj)

        if isinstance(obj, wx.Menu):
            return self.format_menu(obj)

        if isinstance(obj, wx.MenuItem):
            return self.format_menu_item(obj)

        if isinstance(obj, wx.Window):
            return self.FmtWidget(obj)

        elif isinstance(obj, wx.Sizer):
            return self.FmtSizer(obj)

        elif isinstance(obj, wx.SizerItem):
            return self.FmtSizerItem(obj)

        return []

    # noinspection PyProtectedMember
    def format_node(self, obj: Node) -> List[str]:
        # noinspection PyListCreation
        st = [
            "Node:",
            self.Fmt('class', obj.__class__),
            self.Fmt('bases', obj.__class__.__bases__),
            self.Fmt('module', inspect.getmodule(obj))
        ]

        st.append("node_globals:")
        for key, value in obj.node_globals.to_dictionary().items():
            st.append(self.Fmt(key, value))

        if obj._bindings:
            st.append("binding:")
            for binding in obj._bindings:
                self._get_binding(binding, st)

        return st

    # noinspection PyProtectedMember
    def _get_binding(self, binding, st):
        binding_name = binding.__class__.__name__
        if isinstance(binding, ExpressionBinding):
            target = self._get_target(binding._target)
            source = binding._expression.code
            st.append(f'    {binding_name}: {target} <= {source}')
        elif isinstance(binding, ObservableBinding):
            target = self._get_target(binding._target)
            source = f'{binding._observable.__class__.__name__}.{binding._prop}'
            st.append(f'    {binding_name}: {target} <= {source}')
        elif isinstance(binding, EventBinding):
            target = self._get_target(binding._target)
            source = self._evt_names[binding._event.typeId]
            st.append(f'    {binding_name}: {target} <= {source}')
        elif isinstance(binding, TwoWaysBinding):
            self._get_binding(binding._one, st)
            self._get_binding(binding._two, st)
        else:
            st.append(f'    {binding_name}')

    # noinspection PyProtectedMember
    @staticmethod
    def _get_target(target) -> str:
        if isinstance(target, PropertyTarget):
            return f'{target.inst.__class__.__name__}.{target.prop}'
        if isinstance(target, FunctionTarget):
            return str(target.func)
        if isinstance(target, PropertyExpressionTarget):
            return target._expression_code
        if isinstance(target, GlobalValueExpressionTarget):
            return f'node_globals["{target._key}"]'
        return target.__class__.__name__

    def format_menu_bar(self, obj: wx.MenuBar):
        st = ["MenuBar:"]
        if hasattr(obj, 'GetName'):
            st.append(self.Fmt('name', obj.GetName()))
        st.append(self.Fmt('class', obj.__class__))
        st.append(self.Fmt('bases', obj.__class__.__bases__))
        st.append(self.Fmt('module', inspect.getmodule(obj)))
        st.append(self.Fmt('id', obj.GetId()))
        return st

    def format_menu(self, obj: wx.Menu):
        st = [
            "Menu:",
            self.Fmt('class', obj.__class__),
            self.Fmt('bases', obj.__class__.__bases__),
            self.Fmt('module', inspect.getmodule(obj)),
            self.Fmt('style', obj.GetStyle()),
            self.Fmt('title', obj.GetTitle())]
        return st

    def format_menu_item(self, obj: wx.MenuItem):
        st = [
            "MenuItem:",
            self.Fmt('class', obj.__class__),
            self.Fmt('bases', obj.__class__.__bases__),
            self.Fmt('module', inspect.getmodule(obj)),
            self.Fmt('id', obj.GetId()),
            self.Fmt('label', obj.GetLabel()),
            self.Fmt('kind', obj.GetKind())]
        return st
