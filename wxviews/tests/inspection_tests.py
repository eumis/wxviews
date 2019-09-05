from unittest.mock import patch, Mock, call

from pytest import fixture, mark

from wxviews import inspection
from wxviews.inspection import ViewInspectionFrame, ViewInspectionTool
from wxviews.inspection import ViewInspectionTree, ViewInspectionInfoPanel
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


class Item:
    def __init__(self, parent, name=None):
        self.parent: str = parent
        self.name: str = name

    def __eq__(self, other):
        return self.parent == other.parent and self.name == other.name


def _node(name, children=None):
    node = WidgetNode(name, Mock())
    node._children = children if children else []
    return node


@mark.usefixtures('tree_fixture')
class ViewInspectionTreeTests:
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
        """should set app node as tree root"""
        self.tree.BuildTree(WidgetNode(Mock(), Mock()))

        # noinspection PyProtectedMember
        assert self.tree.AddRoot.call_args == call(self.tree._get_node_name(self.root))
        assert self.tree.SetItemData.call_args_list[0] == call(self.root_item, self.root)
        assert self.tree.roots == [self.root_item]

    # pylint: disable=bad-continuation
    @mark.parametrize('children, items', [
        ([], []),
        ([_node('1')], [Item('root', '1')]),
        ([_node('1'), _node('2')], [Item('root', '1'), Item('root', '2')]),
        ([
             _node('1', [_node('1.1'), _node('1.2')]),
             _node('2', [_node('2.1')])
         ],
         [
             Item('root', '1'),
             Item('1', '1.1'), Item('1', '1.2'),
             Item('root', '2'),
             Item('2', '2.1')
         ]),
        ([
             _node('1', [_node('1.1')]),
             _node('2', [
                 _node('2.1', [_node('2.1.1')]),
                 _node('2.2', [_node('2.2.1'), _node('2.2.2')]),
             ])
         ],
         [
             Item('root', '1'), Item('1', '1.1'),
             Item('root', '2'),
             Item('2', '2.1'), Item('2.1', '2.1.1'),
             Item('2', '2.2'), Item('2.2', '2.2.1'), Item('2.2', '2.2.2')
         ])
    ])
    def test_adds_children(self, children, items):
        """Should add node children to tree"""
        actual_items = []
        self.root._children = children
        self.root._instance = 'root'
        self.tree.AddRoot.side_effect = lambda name: Item('')
        self.tree.AppendItem.side_effect = lambda parent, text: Item(parent.name)
        self.tree.SetItemData.side_effect = lambda item, node: self._set_item_data(item, node, actual_items)

        self.tree.BuildTree(self.root)

        assert actual_items == [Item('', 'root')] + items

    @staticmethod
    def _set_item_data(item, node, items):
        item.name = node.instance
        items.append(item)

    def test_selects_obj(self):
        """should select start node"""
        node = WidgetNode(Mock(), Mock())
        self.tree.BuildTree(node)

        assert self.tree.SelectObj.call_args == call(node)

    def test_sets_built_flag(self):
        """should set built flag to true"""
        self.tree.BuildTree(WidgetNode(Mock(), Mock()))

        assert self.tree.built

    @mark.parametrize('start_widget, include_sizers, expand_frame', [
        (Mock(), False, True),
        (Item(''), True, False),
        (Mock(), True, True),
        (Item('root'), False, False)
    ])
    def test_builds_widget_tree_for_widget(self, start_widget, include_sizers, expand_frame):
        """should build default widget tree if passed object other then Node"""
        self.tree.BuildTree(start_widget, include_sizers, expand_frame)

        assert self.super_build.call_args == call(start_widget, includeSizers=include_sizers, expandFrame=expand_frame)


@fixture
def info_fixture(request):
    with patch(f'{inspection.__name__}.InspectionInfoPanel.__init__'):
        with patch(f'{inspection.__name__}.InspectionInfoPanel.UpdateInfo') as super_update_info:
            request.cls.result = None
            info = ViewInspectionInfoPanel()
            info.SetText = Mock()
            info.SetText.side_effect = lambda text, test=request.cls: setattr(test, 'result', text)
            info.SetReadOnly = Mock()

            request.cls.info = info
            request.cls.super_update_info = super_update_info
            yield super_update_info


@mark.usefixtures('info_fixture')
class ViewInspectionInfoPanelTests:
    """ViewInspectionInfoPanel tests"""

    def test_checks_object_none(self):
        """Should set message that object is None"""
        self.info.UpdateInfo(None)

        assert self.result == 'Item is None or has been destroyed.'

    @mark.parametrize('obj', [Mock(), Item('')])
    def test_uses_super_info(self, obj):
        """should use super().UpdateInfo() for object other than Node"""
        self.info.UpdateInfo(obj)

        assert self.super_update_info.call_args == call(obj)

    @mark.parametrize('error', [RuntimeError()])
    def test_handles_error(self, error: Exception):
        """should handle errors and say that can't show info"""
        self.super_update_info.side_effect = lambda obj: self._raise(error)
        self.info.UpdateInfo(Mock())

        assert self.result.startswith(f'Failed to show info.')

    @staticmethod
    def _raise(error):
        raise error
