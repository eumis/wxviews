from math import floor
from unittest.mock import Mock, call, patch

from pytest import mark

from wxviews import containers
from wxviews.containers import Container, render_container_children
from wxviews.containers import View, render_view_children, rerender_on_view_change
from wxviews.containers import For, render_for_items, rerender_on_items_change
from wxviews.containers import If, render_if, rerender_on_condition_change


@mark.parametrize('nodes', [
    [],
    ['item1'],
    ['item1', 'item2']
])
def test_render_container_children(nodes):
    """should render all xml children for every item"""
    with patch(containers.__name__ + '.render_children') as render_children_mock:
        with patch(containers.__name__ + '.InheritedDict') as InheritedDictMock:
            xml_node = Mock(children=nodes)
            node = Container(xml_node)
            parent = Mock()
            child_globals = Mock()
            InheritedDictMock.side_effect = lambda globs: child_globals
            sizer = Mock()
            child_args = {
                'parent_node': node,
                'parent': parent,
                'node_globals': child_globals,
                'sizer': sizer
            }

            render_container_children(node, parent=parent, sizer=sizer)

            assert render_children_mock.call_args == call(node, **child_args)


class ViewTests:
    """View node class tests"""

    @staticmethod
    def test_name_is_none_by_default():
        """name should be None by default"""
        view = View(Mock())

        assert view.name is None

    @staticmethod
    @mark.parametrize('old_name, new_name', [
        (None, 'name'),
        ('name', 'another name')
    ])
    def test_called_on_name_changed(old_name, new_name):
        """should call name_changed on name change"""
        view = View(Mock())
        view.name = old_name
        view.name_changed = Mock()

        view.name = new_name

        assert view.name_changed.call_args == call(view, new_name, old_name)


class RenderViewChildrenTests:
    """render_view_children tests"""

    @staticmethod
    @patch(containers.__name__ + '.render_view')
    def test_renders_view(render_view: Mock):
        """should render view by node name and set result as view child"""
        view_name = 'name'
        child = Mock()
        render_view.side_effect = lambda name, **args: child if name == view_name else None

        node = View(Mock())
        node.name = view_name

        render_view_children(node)

        assert node.children[-1] == child

    @staticmethod
    @patch(containers.__name__ + '.render_view')
    @patch(containers.__name__ + '.InheritedDict')
    def test_renders_view_with_args(inherit_dict: Mock, render_view: Mock):
        """should render view by node name and set result as view child"""
        view_name = 'name'
        inherit_dict.side_effect = lambda source: source

        node = View(Mock())
        node.name = view_name
        parent = Mock()
        sizer = Mock()
        args = {
            'parent_node': node,
            'parent': parent,
            'node_globals': inherit_dict(node.node_globals),
            'sizer': sizer
        }

        render_view_children(node, parent=parent, sizer=sizer)

        assert render_view.call_args == call(view_name, **args)

    @staticmethod
    @mark.parametrize('view_name', ['', None])
    def test_not_render_empty_view_name(view_name):
        """should not render view if name is empty or None"""
        with patch(containers.__name__ + '.render_view') as render_view_mock:
            node = Mock()
            node.set_content = Mock()
            node.name = view_name

            render_view_children(node)

            assert not render_view_mock.called


class RerenderOnViewChangeTests:
    """rerender_on_view_change tests"""

    @staticmethod
    @mark.parametrize('view, new_view, args', [
        ('', 'view', {}),
        ('', 'view', {'parent': Mock()}),
        (None, 'view', {'parent': Mock(), 'sizer': Mock()}),
        ('view', 'new view', {}),
        ('view', 'new view', {'parent': Mock()})
    ])
    def test_renders_new_view(view, new_view, args: dict):
        """should be called on view change"""
        with patch(containers.__name__ + '.render_view_children') as render_view_children_mock:
            node = View(Mock())
            node.view = view

            rerender_on_view_change(node, **args)
            node.name = new_view

            assert render_view_children_mock.call_args == call(node, **args)

    @staticmethod
    @mark.parametrize('view, new_view', [
        ('view', None),
        ('view', ''),
        ('', 'view'),
        (None, 'view'),
        ('view', 'another view')
    ])
    def test_destroys_children(view, new_view):
        """destroy_children should be called on view change"""
        with patch(containers.__name__ + '.render_view_children'):
            node = View(Mock())
            node.name = view
            node.destroy_children = Mock()

            rerender_on_view_change(node)
            node.name = new_view

            assert node.destroy_children.called

    @staticmethod
    @mark.parametrize('empty_view_name', ['', None])
    def test_not_render_empty_name(empty_view_name):
        """should not render in case name is not set or empty"""
        with patch(containers.__name__ + '.render_view') as render_view_mock:
            node = View(Mock())
            node.set_content = Mock()
            node.name = 'view'

            rerender_on_view_change(node, **{})
            node.name = empty_view_name

            assert not (render_view_mock.called or node.set_content.called)

    @staticmethod
    @mark.parametrize('view, new_view', [
        (None, ''),
        ('', None),
        ('', ''),
        (None, None),
        ('view', 'view')
    ])
    def test_not_rerender_same_view(view, new_view):
        """should do nothing if same view is set"""
        with patch(containers.__name__ + '.render_view_children') as render_view_children_mock:
            node = View(Mock())
            node.destroy_children = Mock()
            node.name = view
            parent = Mock()

            rerender_on_view_change(node, parent=parent)
            node.name = new_view

            assert not node.destroy_children.called
            assert not render_view_children_mock.called
            assert not parent.Layout.called

    @staticmethod
    @mark.parametrize('view, new_view', [
        ('view', 'new view'),
        ('', 'view'),
        (None, 'view')
    ])
    def test_calls_parent_layout(view, new_view):
        """should call parent Layout method"""
        with patch(containers.__name__ + '.render_view_children'):
            node = View(Mock())
            node.view = view
            parent = Mock()

            rerender_on_view_change(node, parent=parent)
            node.name = new_view

            assert parent.Layout.called


class ForTests:
    """For node class tests"""

    @staticmethod
    def test_items_is_empty_by_default():
        """items should be empty by default"""
        node = For(Mock())

        assert node.items == []

    @staticmethod
    @mark.parametrize('old_items, new_items', [
        ([], [Mock()]),
        ([Mock()], []),
        ([Mock()], [Mock(), Mock()])
    ])
    def test_called_on_items_changed(old_items, new_items):
        """should call items_changed on items change"""
        node = For(Mock())
        node.items = old_items
        node.items_changed = Mock()

        node.items = new_items

        assert node.items_changed.call_args == call(node, new_items, old_items)

    @staticmethod
    @mark.parametrize('items, nodes, expected_children', [
        ([], [], []),
        (['item1'], ['node1'], ['node1']),
        (['item1'], ['node1', 'node2'], ['node1', 'node2']),
        (['item1', 'item2'], ['node1'], ['node1', 'node1']),
        (['item1', 'item2'], ['node1', 'node2'], ['node1', 'node2', 'node1', 'node2'])
    ])
    def test_renders_children_for_every_item(items, nodes, expected_children):
        """should render all xml children for every item"""
        with patch(containers.__name__ + '.render') as render_mock:
            xml_node = Mock(children=nodes)
            node = For(xml_node)
            node.items = items
            render_mock.side_effect = lambda xmlnode, **args: xmlnode

            render_for_items(node)

            assert node.children == expected_children

    @staticmethod
    @mark.parametrize('items, nodes, expected_children', [
        ([], [], []),
        (['item1'], ['node1'], [(0, 'item1')]),
        (['item1'], ['node1', 'node2'], [(0, 'item1'), (0, 'item1')]),
        (['item1', 'item2'], ['node1'], [(0, 'item1'), (1, 'item2')]),
        (['item1', 'item2'], ['node1', 'node2'],
         [(0, 'item1'), (0, 'item1'), (1, 'item2'), (1, 'item2')])
    ])
    def test_adds_item_and_index_to_globals(items, nodes, expected_children):
        """should add item and index to child globals"""
        with patch(containers.__name__ + '.render') as render_mock:
            xml_node = Mock(children=nodes)
            node = For(xml_node)
            node.items = items
            render_mock.side_effect = lambda *_, **args: \
                (args['node_globals']['index'], args['node_globals']['item'])

            render_for_items(node)

            assert node.children == expected_children

    def _setup_node(self, xml_child_count, items_count, render):
        xml_node = Mock(children=self._get_mock_items(xml_child_count))
        node = For(xml_node)
        node.items = self._get_mock_items(items_count)
        node.add_children([Mock(destroy=Mock(), node_globals={})
                           for _ in range(xml_child_count * items_count)])
        render.side_effect = lambda *_, **__: Mock()
        return node

    @staticmethod
    def _get_mock_items(items_count):
        return [Mock() for _ in range(items_count)]

    @mark.parametrize('xml_child_count, items_count, new_items_count', [
        (2, 4, 4),
        (2, 4, 2),
        (1, 4, 2),
        (4, 3, 0),
        (1, 3, 0),
        (3, 10, 1)
    ])
    def test_destroys_overflow_children(self, xml_child_count, items_count, new_items_count):
        """should destroy overflow children"""
        with patch(containers.__name__ + '.render') as render_mock:
            node = self._setup_node(xml_child_count, items_count, render_mock)

            to_destroy = node.children[xml_child_count * new_items_count:]
            to_left = node.children[:xml_child_count * new_items_count]

            rerender_on_items_change(node)
            node.items = self._get_mock_items(new_items_count)

            for child in to_destroy:
                assert child.destroy.called
            assert node.children == to_left

    @mark.parametrize('xml_child_count, items_count, new_items_count', [
        (2, 4, 4),
        (2, 0, 4),
        (2, 4, 2),
        (2, 4, 6),
        (1, 4, 2),
        (4, 3, 0),
        (1, 3, 0),
        (3, 10, 11)
    ])
    def test_updates_items(self, xml_child_count, items_count, new_items_count):
        """should update item in globals for every children"""
        with patch(containers.__name__ + '.render') as render_mock:
            node = self._setup_node(xml_child_count, items_count, render_mock)
            children_to_update = node.children[:xml_child_count * new_items_count]

            rerender_on_items_change(node)
            node.items = self._get_mock_items(new_items_count)

            for i, child in enumerate(children_to_update):
                item = node.items[floor(i / xml_child_count)]
                assert child.node_globals['item'] == item

    @mark.parametrize('xml_child_count, items_count, new_items_count', [
        (2, 4, 6),
        (2, 4, 10),
        (1, 4, 4)
    ])
    def test_creates_new_children(self, xml_child_count, items_count, new_items_count):
        """should create new children on items change"""
        with patch(containers.__name__ + '.render') as render_mock:
            node = self._setup_node(xml_child_count, items_count, render_mock)

            rerender_on_items_change(node)
            node.items = self._get_mock_items(new_items_count)

            assert len(node.children) == xml_child_count * new_items_count

    @mark.parametrize('expected_args', [
        {},
        {'parent': Mock()},
        {'parent': Mock(), 'sizer': Mock()},
    ])
    def test_passes_args_to_new_children(self, expected_args: dict):
        """should create new children on items change"""
        with patch(containers.__name__ + '.render') as render_mock:
            node = self._setup_node(1, 0, render_mock)
            render_mock.side_effect = lambda n, **args: args

            rerender_on_items_change(node, **expected_args)
            node.items = self._get_mock_items(1)

            assert node.children[0].items() >= expected_args.items()

    @mark.parametrize('xml_child_count, items_count, new_items_count', [
        (2, 4, 6),
        (2, 4, 10),
        (1, 4, 4),
        (2, 4, 2),
        (4, 3, 0),
        (1, 3, 0),
        (3, 10, 11),
        (3, 10, 1)
    ])
    def test_calls_parent_layout(self, xml_child_count, items_count, new_items_count):
        """should call parent Layout"""
        with patch(containers.__name__ + '.render') as render_mock:
            node = self._setup_node(xml_child_count, items_count, render_mock)
            parent = Mock()

            rerender_on_items_change(node, parent=parent)
            node.items = self._get_mock_items(new_items_count)

            assert parent.Layout.called


class IfTests:
    """If node tests"""

    @staticmethod
    def test_condition_is_false_by_default():
        """condition should be False by default"""
        node = If(Mock())

        assert not node.condition

    @staticmethod
    @mark.parametrize('old_condition, new_condition', [
        (False, True),
        (True, False)
    ])
    def test_called_on_condition_changed(old_condition, new_condition):
        """should call condition_changed on condition change"""
        node = If(Mock())
        node.condition = old_condition
        node.condition_changed = Mock()

        node.condition = new_condition

        assert node.condition_changed.call_args == call(node, new_condition, old_condition)

    @staticmethod
    @mark.parametrize('condition', [True, False])
    def test_renders_children(condition):
        """should render children if condition is True"""
        with patch(containers.__name__ + '.render_children') as render_children_mock:
            render_children_mock.reset_mock()
            node = If(Mock())
            node.condition = condition

            render_if(node)

            assert render_children_mock.called == condition

    @staticmethod
    @mark.parametrize('expected_args', [
        {},
        {'parent': Mock()},
        {'parent': Mock(), 'sizer': Mock()},
    ])
    def test_renders_children_if_changed_to_true(expected_args):
        """should render children if condition is changed to True"""

        with patch(containers.__name__ + '.render_children') as render_children:
            node = If(Mock())
            node.condition = False

            rerender_on_condition_change(node, **expected_args)
            node.condition = True

            assert render_children.call_args[-1].items() >= expected_args.items()

    @staticmethod
    @patch(containers.__name__ + '.render_children')
    def test_destroy_children(_: Mock):
        """should destroy children if condition is changed to False"""
        node = If(Mock())
        node.condition = True
        node.destroy_children = Mock()

        rerender_on_condition_change(node)
        node.condition = False

        assert node.destroy_children

    @staticmethod
    @mark.parametrize('new_condition', [True, False])
    def test_calls_parent_layout(new_condition):
        """should call parent Layout method"""
        with patch(containers.__name__ + '.render_children'):
            node = If(Mock())
            node.condition = not new_condition
            parent = Mock()

            rerender_on_condition_change(node, parent=parent)
            node.condition = new_condition

            assert parent.Layout.called
