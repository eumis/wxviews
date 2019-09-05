from collections import Callable

from pylint.lint import PyLinter

TESTS_DISABLED = ['line-too-long',
                  'missing-docstring',
                  'invalid-name',
                  'no-member',
                  'protected-access',
                  'too-few-public-methods',
                  'super-init-not-called',
                  'broad-except']


def register(linter: PyLinter):
    msg_ids = _get_msg_ids(linter)
    base = linter.add_one_message
    linter.add_one_message = lambda *args: add_one_message(*args, linter=linter, base=base,
                                                           msg_ids=msg_ids)


def _get_msg_ids(linter: PyLinter):
    msg_ids = []
    for msg_symbol in TESTS_DISABLED:
        for msg_def in linter.msgs_store.get_message_definitions(msg_symbol):
            msg_ids.append(msg_def.msgid)
    return msg_ids


def add_one_message(message_definition, line, node, args, confidence, col_offset,
                    linter: PyLinter = None, base: Callable = None, msg_ids=None):
    if message_definition.symbol == 'no-name-in-module' and node is not None and 'wx' in args:
        return
    if linter.current_name and 'test' in linter.current_name and message_definition.msgid in msg_ids:
        return
    base(message_definition, line, node, args, confidence, col_offset)
