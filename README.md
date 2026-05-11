# jpq

`jq`-style JSON filtering, but with Python expressions.

The parsed stdin JSON is bound to `this`; the value of the expression is printed as JSON.

## Install

From source, after cloning:

```bash
uv tool install .
```

Or run straight from the checkout without (re)installing:

```bash
echo '{"name":"alice"}' | uv run main.py 'this["name"]'
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

## Advanced examples

Pipe an API response through a multi-line expression to reshape it:

```bash
curl -s https://api.github.com/repos/python/cpython | jpq '
{
"stars": this["stargazers_count"],
"last_pushed_seconds_ago": (
    datetime.datetime.now(tz=datetime.UTC)
    - datetime.datetime.fromisoformat(this["pushed_at"])
).total_seconds()
}'
# {"stars": 72644, "last_pushed_seconds_ago": 2168.664175}
```

Read environment variables:
```bash
export PASS=secret123
echo '{"url": "postgres://user:pass@host:port/db"}' | jpq 'this["url"].replace("pass", env("PASS"))'
# "postgres://user:secret123@host:port/db"
```
Here `env("PASS")` is equivalent to `os.environ["PASS"]` (see [helpers.py](src/jpq/helpers.py)).
