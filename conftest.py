from injectool import Container, set_default_container, use_container
from pytest import fixture


def pytest_configure(config):
    set_default_container(Container())


@fixture
def container_fixture(request):
    """runs test in own dependency container"""
    with use_container() as container:
        if request.cls:
            request.cls.container = container
        yield container
