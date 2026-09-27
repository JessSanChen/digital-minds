"""Runs the model's code like a code-interpreter cell: if the last statement is
an expression, its value is printed (the pilot showed models writing
notebook-style code whose final `result` line would otherwise print nothing).
Tracebacks are trimmed to the user's own frames."""

import ast
import sys
import traceback

path = sys.argv[1]
source = open(path).read()
namespace = {"__name__": "__main__"}
try:
    tree = ast.parse(source, path)
    last = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
    exec(compile(tree, path, "exec"), namespace)
    if last is not None:
        value = eval(compile(ast.Expression(last.value), path, "eval"), namespace)
        if value is not None:
            print(repr(value))
except SyntaxError:
    traceback.print_exc(limit=0)
    sys.exit(1)
except BaseException as e:  # noqa: BLE001 - report exactly like python would
    if isinstance(e, SystemExit):
        raise
    traceback.print_exception(type(e), e, e.__traceback__.tb_next)
    sys.exit(1)
