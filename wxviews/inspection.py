import inspect
import sys
from typing import Any, Union, List

from pyviews.core import Node, InstanceNode
import wx
from wx import Frame, Sizer
from wx import Point, DefaultPosition, Size
from wx.aui import AuiManager, AUI_MGR_DEFAULT, AUI_MGR_TRANSPARENT_DRAG, AUI_MGR_ALLOW_ACTIVE_PANE, AuiPaneInfo
from wx.lib.agw.customtreectrl import GenericTreeItem
from wx.lib.inspection import InspectionTree, InspectionFrame, InspectionInfoPanel, Icon

from wxviews.widgets import WidgetNode, get_root


class ViewInspectionTool:
    """
    The :class:`ViewInspectionTool` is a singleton that manages creating and
    showing an :class:`ViewInspectionFrame`.
    """

    # Note: This is the Borg design pattern which ensures that all
    # instances of this class are actually using the same set of
    # instance data.  See
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/66531
    __shared_state = None

    # noinspection PyTypeChecker
    def __init__(self):
        if not ViewInspectionTool.__shared_state:
            ViewInspectionTool.__shared_state = self.__dict__
        else:
            self.__dict__ = ViewInspectionTool.__shared_state

        if not hasattr(self, 'initialized'):
            self.initialized = False
            self._frame: ViewInspectionFrame = None
            self._pos: Point = DefaultPosition
            self._size: Size = Size(850, 700)
            self._config = None
            self._locals: dict = {}
            self._app: WidgetNode = None

    def init(self, pos: Point = DefaultPosition, size: Size = Size(850, 700),
             config=None, crust_locals: dict = None, app: WidgetNode = None):
        """
        Init is used to set some parameters that will be used later
        when the inspection tool is shown.  Suitable defaults will be
        used for all of these parameters if they are not provided.

        :param pos:   The default position to show the frame at
        :param size:  The default size of the frame
        :param config: A :class:`Config` object to be used to store layout
            and other info to when the inspection frame is closed.
            This info will be restored the next time the inspection
            frame is used.
        :param crust_locals: A dictionary of names to be added to the PyCrust
            namespace.
        :param app:  A reference to the :class:`App` object.
        """
        self._frame = None
        self._pos = pos
        self._size = size
        self._config = config
        self._locals = crust_locals
        self._app = app
        if not self._app:
            self._app = get_root()
        self.initialized = True

    def show(self, select_obj: Any = None, refresh_tree: bool = False):
        """
        Creates the inspection frame if it hasn't been already, and
        raises it if neccessary.

        :param select_obj: Pass a widget or sizer to have that object be
                     preselected in widget tree.
        :param boolean refresh_tree: rebuild the widget tree, default False

        """
        if not self.initialized:
            self.init()

        parent = self._app.instance.GetTopWindow()
        if not select_obj:
            select_obj = parent
        if not self._frame:
            self._frame = ViewInspectionFrame(parent=parent,
                                              pos=self._pos,
                                              size=self._size,
                                              config=self._config,
                                              crust_locals=self._locals,
                                              app=self._app)
        if select_obj:
            self._frame.SetObj(select_obj)
        if refresh_tree:
            self._frame.RefreshTree()
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

    def __init__(self, wnd=None, crust_locals=None, config=None,
                 app=None, title="Wxviews Inspection Tool",
                 *args, **kw):
        kw['title'] = title
        Frame.__init__(self, *args, **kw)

        self.SetExtraStyle(wx.WS_EX_BLOCK_EVENTS)
        self.includeSizers = False
        self.started = False

        self.SetIcon(Icon.GetIcon())
        self.MakeToolBar()
        panel = wx.Panel(self, size=self.GetClientSize())

        # tell FrameManager to manage this frame
        self.mgr = AuiManager(panel, AUI_MGR_DEFAULT | AUI_MGR_TRANSPARENT_DRAG | AUI_MGR_ALLOW_ACTIVE_PANE)

        # make the child tools
        self.tree = ViewInspectionTree(panel, size=(100, 300))
        self.info = ViewInspectionInfoPanel(panel, style=wx.NO_BORDER)

        if not crust_locals:
            crust_locals = {}
        myIntroText = (
                "Python %s on %s, wxPython %s\n"
                "NOTE: The 'obj' variable refers to the object selected in the tree."
                % (sys.version.split()[0], sys.platform, wx.version()))
        self.crust = wx.py.crust.Crust(panel, locals=crust_locals,
                                       intro=myIntroText,
                                       showInterpIntro=False,
                                       style=wx.NO_BORDER,
                                       )
        self.locals = self.crust.shell.interp.locals
        self.crust.shell.interp.introText = ''
        self.locals['obj'] = self.obj = wnd
        self.locals['app'] = app
        self.locals['wx'] = wx
        wx.CallAfter(self._postStartup)

        # put the chlid tools in AUI panes
        self.mgr.AddPane(self.info,
                         AuiPaneInfo().Name("info").Caption("Object Info").
                         CenterPane().CaptionVisible(True).
                         CloseButton(False).MaximizeButton(True)
                         )
        self.mgr.AddPane(self.tree,
                         AuiPaneInfo().Name("tree").Caption("Widget Tree").
                         CaptionVisible(True).Left().Dockable(True).Floatable(True).
                         BestSize((280, 200)).CloseButton(False).MaximizeButton(True)
                         )
        self.mgr.AddPane(self.crust,
                         AuiPaneInfo().Name("crust").Caption("PyCrust").
                         CaptionVisible(True).Bottom().Dockable(True).Floatable(True).
                         BestSize((400, 200)).CloseButton(False).MaximizeButton(True)
                         )

        self.mgr.Update()

        if config is None:
            config = wx.Config('wxpyinspector')
        self.config = config
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        if self.Parent:
            tlw = self.Parent.GetTopLevelParent()
            tlw.Bind(wx.EVT_CLOSE, self.OnClose)
        self.LoadSettings(self.config)
        self.crust.shell.lineNumbers = False
        self.crust.shell.setDisplayLineNumbers(False)
        self.crust.shell.SetMarginWidth(1, 0)


class ViewInspectionTree(InspectionTree):
    def BuildTree(self, startWidget: Node, includeSizers=False, expandFrame=False):
        """setup root"""
        if self.GetCount():
            self.DeleteAllItems()
            self.roots = []
            self.built = False

        realRoot = self.AddRoot('Top-level Windows')

        root_node = get_root()

        for child in root_node.children:
            root = self.add_node(realRoot, child)
            self.roots.append(root)

        # Expand the subtree containing the startWidget, and select it.
        self.built = True
        self.SelectObj(startWidget)

    def add_node(self, parentItem: GenericTreeItem, node: Union[Node, InstanceNode]) -> GenericTreeItem:
        text = node.__class__.__name__
        item = self.AppendItem(parentItem, text)
        self.SetItemData(item, node)
        self.SetItemTextColour(item, "green")

        try:
            if hasattr(node.instance, 'GetName'):
                self.SetItemText(item, f'{text}({node.instance.GetName()})')
            else:
                self.SetItemText(item, f'{text}({node.instance.__class__.__name__})')
            if isinstance(node.instance, Sizer):
                self._AddSizer(item, node.instance)
            else:
                self._AddWidget(item, node.instance, False)
        except AttributeError:
            pass

        for binding in node._bindings:
            self._add_binding(item, binding)

        for child in node.children:
            self.add_node(item, child)

        return item

    def _AddWidget(self, parentItem, widget, includeSizers) -> GenericTreeItem:
        text = self.GetTextForWidget(widget)
        item = self.AppendItem(parentItem, text)
        self.SetItemData(item, widget)
        return item

    def _AddSizer(self, parentItem, sizer):
        text = self.GetTextForSizer(sizer)
        item = self.AppendItem(parentItem, text)
        self.SetItemData(item, sizer)
        self.SetItemTextColour(item, "blue")
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

        elif isinstance(obj, wx.Window):
            st += self.FmtWidget(obj)

        elif isinstance(obj, wx.Sizer):
            st += self.FmtSizer(obj)

        elif isinstance(obj, wx.SizerItem):
            st += self.FmtSizerItem(obj)

        else:
            st += self.format_node(obj)

        self.SetReadOnly(False)
        self.SetText('\n'.join(st))
        self.SetReadOnly(True)

    def format_node(self, obj: Node) -> List[str]:
        st = ["Widget:"]
        st.append(self.Fmt('class', obj.__class__))
        st.append(self.Fmt('bases', obj.__class__.__bases__))
        st.append(self.Fmt('module', inspect.getmodule(obj)))
        return st
