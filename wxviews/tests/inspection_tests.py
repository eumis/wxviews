from unittest.mock import patch, Mock, call

from pytest import fixture, mark

from wxviews import inspection
from wxviews.inspection import ViewInspectionFrame, ViewInspectionTool, ViewInspectionTree
from wxviews.widgets import WidgetNode


@fixture
def tool_fixture(request):
    with patch(f'{inspection.__name__}.get_root') as get_root:
        root = WidgetNode(Mock(), Mock())
        top_window = Mock()
        root.instance.GetTopWindow = Mock()
        root.instance.GetTopWindow.side_effect = lambda: top_window
        get_root.side_effect = lambda: root

        request.cls.root = root
        request.cls.top_window = top_window
        with patch(f'{inspection.__name__}.{ViewInspectionFrame.__name__}') as frame_init:
            frame = Mock()
            frame_init.side_effect = lambda *a, **kw: frame
            request.cls.frame_init = frame_init
            request.cls.frame = frame
            request.cls.tool = ViewInspectionTool()
            yield frame_init


@mark.usefixtures('tool_fixture')
class ViewInspectionToolTests:
    """ViewInspectionTool tests"""

    def test_creates_frame(self):
        """should create frame with parameters"""
        pos = Mock()
        size = Mock()
        config = Mock()
        crust_locals = Mock()
        tool = ViewInspectionTool(pos=pos, size=size, config=config, crust_locals=crust_locals)

        tool.show()

        assert self.frame_init.call_args == call(parent=self.top_window, pos=pos, size=size, config=config,
                                                 locals=crust_locals, app=self.root.instance, root=self.root)

    @mark.parametrize('select_obj', [None, Mock()])
    def test_sets_passed_object(self, select_obj):
        """should create frame with parameters"""
        expected = select_obj if select_obj else self.root

        self.tool.show(select_obj)

        assert self.frame.SetObj.call_args == call(expected)

    @mark.parametrize('select_obj', [None, Mock()])
    def test_shows_frame(self, select_obj):
        """should create frame with parameters"""
        expected = select_obj if select_obj else self.root

        self.tool.show(select_obj)

        assert self.frame.Show.called
        assert self.frame.Raise.called


@fixture
def frame_fixture(request):
    with patch(f'{inspection.__name__}.InspectionFrame.__init__') as frame_init:
        frame_init.side_effect = _frame_init
        request.cls.frame_init = frame_init
        yield frame_init


def _frame_init(frame, *_, **__):
    frame.locals = {}


@mark.usefixtures('frame_fixture')
class ViewInspectionFrameTests:
    """ViewInspectionFrame tests"""

    def tests_sets_root_to_locals(self):
        """should add root node to crust locals"""
        pos = Mock()
        size = Mock()
        config = Mock()
        crust_locals = Mock()
        root = Mock()
        parent = Mock()
        app = Mock()

        frame = ViewInspectionFrame(parent=parent,
                                    pos=pos,
                                    size=size,
                                    config=config,
                                    locals=crust_locals,
                                    app=app,
                                    root=root)

        assert self.frame_init.call_args == call(frame, parent=parent, pos=pos, size=size, config=config,
                                                 locals=crust_locals, app=app)
        assert frame.locals['root'] == root


@fixture
def tree_fixture(request):
    with patch(f'{inspection.__name__}.get_root') as get_root:
        root = WidgetNode(Mock(), Mock())
        get_root.side_effect = lambda: root
        request.cls.root = root
        with patch(f'{inspection.__name__}.InspectionTree.__init__') as tree_init:
            tree_init.side_effect = lambda *a, **kw: None
            with patch(f'{inspection.__name__}.InspectionTree.BuildTree') as super_build:
                tree = ViewInspectionTree()
                tree.roots = []
                tree.built = False
                tree.DeleteAllItems = Mock()
                tree.SetItemData = Mock()
                tree.SelectObj = Mock()
                tree.AppendItem = Mock()

                tree.GetCount = Mock()
                tree.GetCount.side_effect = lambda: 0

                root_item = Mock()
                tree.AddRoot = Mock()
                tree.AddRoot.side_effect = lambda *a: root_item

                request.cls.tree = tree
                request.cls.root_item = root_item
                request.cls.super_build = super_build
                yield super_build


@mark.usefixtures('tree_fixture')
class ViewInpsectionTreeTests:
    """ViewInspectionTree tests"""

    @mark.parametrize('items_count, should_clear', [
        (0, False),
        (1, True),
        (5, True)
    ])
    def test_clears_tree_before_build(self, items_count, should_clear):
        """should clear tree before build"""
        self.tree.GetCount.side_effect = lambda c=items_count: c

        self.tree.BuildTree(self.root)

        assert self.tree.DeleteAllItems.called == should_clear

    def test_sets_root_node(self):
        """should create root from application node"""
        self.tree.BuildTree(WidgetNode(Mock(), Mock()))

        assert self.tree.AddRoot.called
        assert self.tree.SetItemData.call_args_list[0] == call(self.root_item, self.root)
