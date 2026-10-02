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

$ echo '{"a": [{"b": 2}]}' | jpq 'this.a[0].b'  # 2

$ echo '[{"status":"ok"},{"status":"error"},{"status":"ok"}]' | jpq 'collections.Counter(el["status"] for el in this)'  # {"ok": 2, "error": 1}
```

Note that you can access `dict` keys as attributes, e.g. `this.name` instead of `this["name"]`.

Missing attributes show the available keys when the object has fewer than 20 keys:

```bash
$ echo '{"name":"alice","age":30}' | jpq 'this.abcd'
jpq: AttributeError: abcd (available keys: ['name', 'age'])
```

You can set the `JPQ_VERBOSE` environment variable to get a full set of available keys when an attribute is missing.

Pre-imported in the eval namespace: `re`, `collections`, `itertools`, `statistics`, `math`, `datetime`, plus all builtins.

Run `jpq --help` for more.
