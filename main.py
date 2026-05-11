#!/usr/bin/env python3
import collections
import datetime
import itertools
import json
import math
import re
import statistics
import sys


HELP = """\
usage: jqpy 'EXPR'

Evaluate a Python expression against JSON read from stdin.
The parsed JSON is bound to the name `this`. The result of EXPR
is printed as JSON.

Available without import:
  re, collections, itertools, statistics, math, datetime
  (plus all builtins: sum, len, min, max, sorted, set, ...)

Examples:
  echo '{"name":"alice","age":30}' | jqpy 'this["name"]'
  # "alice"

  echo '[{"a":1},{"a":2},{"a":-1}]' | jqpy 'sum(el["a"] for el in this if el["a"] < 2)'
  # 0

  echo '[1,2,3,4,5]' | jqpy 'statistics.mean(this)'
  # 3

  echo '[{"k":"a"},{"k":"b"},{"k":"a"}]' | jqpy 'collections.Counter(el["k"] for el in this)'
  # {"a": 2, "b": 1}

  echo '["foo123","bar456"]' | jqpy '[re.sub(r"\\d+","",s) for s in this]'
  # ["foo", "bar"]
"""


# Exit codes
EXIT_USAGE = 2
EXIT_STDIN = 3
EXIT_EVAL = 4
EXIT_OUTPUT = 5


class JqpyError(Exception):
    """Base class for jqpy errors. Subclasses set `exit_code`."""
    exit_code = 1


class StdinError(JqpyError):
    """Input on stdin was not valid JSON (or unreadable)."""
    exit_code = EXIT_STDIN


class EvalError(JqpyError):
    """The expression failed to parse or raised at runtime."""
    exit_code = EXIT_EVAL


class OutputError(JqpyError):
    """The result could not be serialized to JSON."""
    exit_code = EXIT_OUTPUT


def _fallback(o):
    if isinstance(o, (set, frozenset)):
        return list(o)
    if isinstance(o, (datetime.datetime, datetime.date)):
        return o.isoformat()
    try:
        return list(o)
    except TypeError:
        return str(o)


def read_input(stream):
    try:
        return json.load(stream)
    except json.JSONDecodeError as e:
        raise StdinError(f"invalid JSON on stdin: {e}") from e
    except OSError as e:
        raise StdinError(f"could not read stdin: {e}") from e


def evaluate(expr, this):
    env = {
        "__builtins__": __builtins__,
        "re": re,
        "collections": collections,
        "itertools": itertools,
        "statistics": statistics,
        "math": math,
        "datetime": datetime,
    }
    try:
        code = compile(expr, "<expr>", "eval")
    except SyntaxError as e:
        raise EvalError(f"syntax error in expression: {e.msg} (col {e.offset})") from e

    try:
        return eval(code, env, {"this": this})
    except Exception as e:
        raise EvalError(f"{type(e).__name__}: {e}") from e


def write_output(result):
    try:
        return json.dumps(result, indent=2, ensure_ascii=False, default=_fallback)
    except (TypeError, ValueError) as e:
        raise OutputError(f"result is not JSON-serializable: {e}") from e


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        if len(sys.argv) < 2:
            print(HELP, file=sys.stderr)
            sys.exit(EXIT_USAGE)
        print(HELP)
        sys.exit(0)

    expr = sys.argv[1]

    try:
        this = read_input(sys.stdin)
        result = evaluate(expr, this)
        output = write_output(result)
    except JqpyError as e:
        print(f"jqpy: {e}", file=sys.stderr)
        sys.exit(e.exit_code)

    print(output)


if __name__ == "__main__":
    main()
