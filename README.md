# jpq

`jq`-style JSON filtering, but with Python expressions.

The parsed stdin JSON is bound to `this`; the value of the expression is printed as JSON.

## Install
From PyPI using `uv` (recommended):
```bash
uv tool install jpq
# alternatively (using pip/pipx):
# pipx install jpq
# pip install --user jpq
```

From source, after cloning:
```bash
uv tool install .
```

By building locally:
```bash
uv build
uv tool install ./dist/jpq-*.whl
```

Or run straight from the checkout without (re)installing:
```bash
$ echo '[1,2]' | uv run main.py 'this[0]'  # 1
```

## Usage

```bash
$ echo '{"name":"alice","age":30}' | jpq 'this["name"]'  # "alice"

$ echo '[1,2,3,4,5]' | jpq 'statistics.mean(this)'  # 3

$ echo '[{"status":"ok"},{"status":"error"},{"status":"ok"}]' | jpq 'collections.Counter(el["status"] for el in this)'  # {"ok": 2, "error": 1}
```

Pre-imported in the eval namespace: `re`, `collections`, `itertools`, `statistics`, `math`, `datetime`, plus all builtins.

Run `jpq --help` for more.

## Advanced examples

Pipe an API response through a multi-line expression to reshape it:

```bash
$ curl -s https://api.github.com/repos/python/cpython | jpq '
{
"now": (now:=datetime.datetime.now(tz=datetime.UTC)),
"stars": this["stargazers_count"],
"last_pushed_seconds_ago": (
    now - datetime.datetime.fromisoformat(this["pushed_at"])
).total_seconds(),
}'
{
  "now": "2026-05-13T15:05:11.746397+00:00",
  "stars": 72668,
  "last_pushed_seconds_ago": 566.746397
}
```
Note how the walrus operator (`:=`) is used to assign `now` and use it in the expression and how it is serialized to JSON via `datetime` fallback.

See more examples in the [blog post](https://stack.airatvaliullin.com/tools/terminal/jpq/) about `jpq`.
