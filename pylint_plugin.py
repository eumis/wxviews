from os import linesep

from astroid import MANAGER, scoped_nodes, Module
from pylint.lint import PyLinter


def register(_: PyLinter):
    # Needed for registering the plugin.
    pass


def transform(mod: Module):
    stream = mod.stream()
    if not stream:
        return
    with stream:
        try:
            source = stream.read().decode()
            disables = []
            if 'from wx import' in source or f'import wx{linesep}' in source:
                disables.append("no-name-in-module")
            if 'tests' in mod.name:
                disables += ['line-too-long', 'missing-docstring', 'invalid-name', 'no-member', 'protected-access']
            mod.file_bytes = f'{linesep}# pylint: disable={",".join(disables)}{linesep}{source}'.encode()
        except UnicodeDecodeError:
            pass


MANAGER.register_transform(scoped_nodes.Module, transform)
