"""Extension of wxpython InspectionTool to show view nodes"""

from os import linesep
import inspect
from traceback import format_exc
from typing import Any, Union, List
from unittest.mock import patch

from pyviews.binding import ExpressionBinding, ObservableBinding, TwoWaysBinding
from pyviews.core import Node, InstanceNode
import wx
from wx import Point, DefaultPosition, Size, MenuBar
from wx import Menu, MenuItem, Window, Sizer, SizerItem
from wx.lib import inspection
from wx.lib.agw.customtreectrl import GenericTreeItem
from wx.lib.inspection import InspectionTree, InspectionFrame, InspectionInfoPanel

from wxviews.widgets import WxNode, get_root, EventBinding


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
            self._app: WxNode = get_root()

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
        with patch(f'{inspection.__name__}.{InspectionTree.__name__}',
                   ViewInspectionTree):
            with patch(f'{inspection.__name__}.{InspectionInfoPanel.__name__}',
                       ViewInspectionInfoPanel):
                InspectionFrame.__init__(self, *args, **kwargs)
                self.locals['root'] = root


class ViewInspectionTree(InspectionTree):
    """Extends wx.lib.inspection.InspectionTree to show view nodes"""

    # noinspection PyPep8Naming
    def BuildTree(self, startWidget, includeSizers=False, expandFrame=False):
        """setup root"""
        if isinstance(startWidget, Node):
            self.build_node_tree(startWidget)
        else:
            super().BuildTree(startWidget, includeSizers=includeSizers, expandFrame=expandFrame)

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

    def add_node(self,
                 parent_item: GenericTreeItem,
                 node: Union[Node, InstanceNode]) -> GenericTreeItem:
        """Adds node item"""
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


# pylint: disable=protected-access
class ViewInspectionInfoPanel(InspectionInfoPanel):
    """Extends wx.lib.InspectionInfoPanel to show Node info"""

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
                lines = []
                lines += self.format_node(obj)
                if hasattr(obj, 'instance'):
                    lines += self._format_wx_item(obj.instance)
                self._set_text(lines)
            else:
                super().UpdateInfo(obj)
        except RuntimeError:
            self._set_text(['Failed to show info.', format_exc()])

    def _set_text(self, lines: List[str]):
        self.SetReadOnly(False)
        self.SetText(linesep.join(lines))
        self.SetReadOnly(True)

    # pylint:disable=too-many-return-statements
    def _format_wx_item(self, obj: Any) -> List[str]:
        if isinstance(obj, MenuBar):
            return self.format_menu_bar(obj)

        if isinstance(obj, Menu):
            return self.format_menu(obj)

        if isinstance(obj, MenuItem):
            return self.format_menu_item(obj)

        if isinstance(obj, Window):
            return self.FmtWidget(obj)

        if isinstance(obj, Sizer):
            return self.FmtSizer(obj)

        if isinstance(obj, SizerItem):
            return self.FmtSizerItem(obj)

        return []

    # noinspection PyProtectedMember, PyListCreation
    def format_node(self, obj: Node) -> List[str]:
        """Formats Node info"""
        lines = [
            "Node:",
            self.Fmt('class', obj.__class__),
            self.Fmt('bases', obj.__class__.__bases__),
            self.Fmt('module', inspect.getmodule(obj))
        ]

        lines.append("node_globals:")
        for key, value in obj.node_globals.to_dictionary().items():
            lines.append(self.Fmt(key, value))

        if obj._bindings:
            lines.append("binding:")
            for binding in obj._bindings:
                self._get_binding(binding, lines)

        return lines

    # noinspection PyProtectedMember
    def _get_binding(self, binding, lines: List[str]):
        binding_name = binding.__class__.__name__
        if isinstance(binding, ExpressionBinding):
            target = self._get_target(binding._target)
            source = binding._expression.code
            lines.append(f'    {binding_name}: {target} <= {source}')
        elif isinstance(binding, ObservableBinding):
            target = self._get_target(binding._target)
            source = f'{binding._observable.__class__.__name__}.{binding._prop}'
            lines.append(f'    {binding_name}: {target} <= {source}')
        elif isinstance(binding, EventBinding):
            target = self._get_target(binding._callback)
            source = self._evt_names[binding._event.typeId]
            lines.append(f'    {binding_name}: {target} <= {source}')
        elif isinstance(binding, TwoWaysBinding):
            self._get_binding(binding._one, lines)
            self._get_binding(binding._two, lines)
        else:
            lines.append(f'    {binding_name}')

    # noinspection PyProtectedMember
    @staticmethod
    def _get_target(target) -> str:
        # if isinstance(target, PropertyTarget):
        #     return f'{target.inst.__class__.__name__}.{target.prop}'
        # if isinstance(target, FunctionTarget):
        #     return str(target.func)
        # if isinstance(target, PropertyExpressionTarget):
        #     return target._expression_code
        # if isinstance(target, GlobalValueExpressionTarget):
        #     return f'node_globals["{target._key}"]'
        return target.__class__.__name__

    def format_menu_bar(self, obj: MenuBar):
        """Formats MenuItem info"""
        lines = ["MenuBar:"]
        if hasattr(obj, 'GetName'):
            lines.append(self.Fmt('name', obj.GetName()))
        lines.append(self.Fmt('class', obj.__class__))
        lines.append(self.Fmt('bases', obj.__class__.__bases__))
        lines.append(self.Fmt('module', inspect.getmodule(obj)))
        lines.append(self.Fmt('id', obj.GetId()))
        return lines

    def format_menu(self, obj: Menu):
        """Formats Menu info"""
        lines = [
            "Menu:",
            self.Fmt('class', obj.__class__),
            self.Fmt('bases', obj.__class__.__bases__),
            self.Fmt('module', inspect.getmodule(obj)),
            self.Fmt('style', obj.GetStyle()),
            self.Fmt('title', obj.GetTitle())]
        return lines

    def format_menu_item(self, obj: MenuItem):
        """Formats MenuItem info"""
        lines = [
            "MenuItem:",
            self.Fmt('class', obj.__class__),
            self.Fmt('bases', obj.__class__.__bases__),
            self.Fmt('module', inspect.getmodule(obj)),
            self.Fmt('id', obj.GetId()),
            self.Fmt('label', obj.GetLabel()),
            self.Fmt('kind', obj.GetKind())]
        return lines
