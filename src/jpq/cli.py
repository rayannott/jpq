import collections
import datetime
import itertools
import json
import pathlib
import math
import os
import re
import statistics
import sys
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version
from typing import IO, Any

import click

from jpq.exceptions import EvalError, JpqError, OutputError, StdinError


def _get_version() -> str:
    try:
        return pkg_version("jpq")
    except PackageNotFoundError:
        return "unknown"


EPILOG = """\
\b
Available without import:
  re, os, collections, itertools, statistics, math, datetime, pathlib
  (plus all builtins: sum, len, min, max, sorted, set, ...)

\b
Examples:
  $ echo '{"name":"alice","age":30}' | jpq 'this["name"]'
  "alice"

\b
  $ echo '[1,2,3,4,5]' | jpq 'statistics.mean(this)'
  3

\b
  $ echo '["a", "b", "a"]' | jpq 'collections.Counter(this)'
  {"a": 2, "b": 1}

\b
  $ echo '["foo123","bar456"]' | jpq '[re.sub(r"\\d","",s) for s in this]'
  ["foo", "bar"]

\b
  $ echo '"2020-02-28T23:59:59+00:00"' | jpq 'datetime.datetime.fromisoformat(this) + datetime.timedelta(seconds=1)'
  "2020-02-29T00:00:00+00:00"

"""


def _fallback(o: Any) -> Any:
    if isinstance(o, (set, frozenset)):
        return list(o)
    if isinstance(o, (datetime.datetime, datetime.date)):
        return o.isoformat()
    if isinstance(o, pathlib.Path):
        return str(o)
    raise TypeError(f"cannot serialize {type(o).__name__}")


def read_input(stream: IO[str]) -> Any:
    try:
        return json.load(stream)
    except json.JSONDecodeError as e:
        raise StdinError(f"invalid JSON on stdin: {e}") from e
    except OSError as e:
        raise StdinError(f"could not read stdin: {e}") from e


def evaluate(expr: str, this: Any) -> Any:
    env: dict[str, Any] = {
        "__builtins__": __builtins__,
        "re": re,
        "collections": collections,
        "itertools": itertools,
        "statistics": statistics,
        "math": math,
        "datetime": datetime,
        "os": os,
        "pathlib": pathlib,
        "env": lambda name: os.environ[name],
    }
    try:
        code = compile(expr, "<expr>", "eval")
    except SyntaxError as e:
        raise EvalError(f"syntax error in expression: {e.msg} (col {e.offset})") from e

    try:
        return eval(code, env, {"this": this})
    except Exception as e:
        raise EvalError(f"{type(e).__name__}: {e}") from e


def write_output(result: Any, *, compact: bool = False) -> str:
    try:
        if compact:
            return json.dumps(
                result, separators=(",", ":"), ensure_ascii=False, default=_fallback
            )
        return json.dumps(result, indent=2, ensure_ascii=False, default=_fallback)
    except (TypeError, ValueError) as e:
        raise OutputError(f"result is not JSON-serializable: {e}") from e


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    epilog=EPILOG,
)
@click.argument("expr", required=False, default=None)
@click.option(
    "--compact",
    "-c",
    is_flag=True,
    help="Print the result as compact JSON (no indentation).",
)
@click.version_option(
    version=_get_version(), prog_name="jpq", message="jpq %(version)s"
)
def main(expr: str | None, compact: bool) -> None:
    """Evaluate a Python expression against JSON read from stdin.

    The parsed JSON is bound to the name `this`. If EXPR is omitted,
    the identity transform (`this`) is used. The result is printed as JSON.
    """
    # If no expression is provided and stdin is a terminal, print the help and exit.
    if expr is None and sys.stdin.isatty():
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit(2)

    if expr is None:
        expr = "this"

    try:
        this = read_input(sys.stdin)
        result = evaluate(expr, this)
        output = write_output(result, compact=compact)
    except JpqError as e:
        click.echo(f"jpq: {e}", err=True)
        sys.exit(e.exit_code)

    click.echo(output)


if __name__ == "__main__":
    main()  # pyright: ignore[reportCallIssue]  # type: ignore[call-arg]
