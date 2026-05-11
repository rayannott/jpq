# jpq

`jq`-style JSON filtering, but with Python expressions.

The parsed stdin JSON is bound to `this`; the value of the expression is printed as JSON.

## Install

From source, after cloning:

```bash
uv tool install .
```

For local hacking:

```bash
uv tool install --editable .
```

## Usage

```bash
echo '{"name":"alice","age":30}' | jpq 'this["name"]'
# "alice"

echo '[1,2,3,4,5]' | jpq 'statistics.mean(this)'
# 3

echo '[{"k":"a"},{"k":"b"},{"k":"a"}]' | jpq 'collections.Counter(el["k"] for el in this)'
# {"a": 2, "b": 1}
```

Pre-imported in the eval namespace: `re`, `collections`, `itertools`, `statistics`, `math`, `datetime`, plus all builtins.

Run `jpq --help` for more.
