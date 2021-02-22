# pytest-insta

![Build Status](https://github.com/vberlier/pytest-insta/workflows/CI/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/pytest-insta.svg)](https://pypi.org/project/pytest-insta/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytest-insta.svg)](https://pypi.org/project/pytest-insta/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

> A practical snapshot testing plugin for pytest.

<img align="right" width="50%" src="https://raw.githubusercontent.com/vberlier/pytest-insta/main/demo.svg?sanitize=true">

```python
assert snapshot() == "awesome!"
```

## Introduction

Snapshot testing makes it easy to monitor and approve changes by comparing the result of an operation against a previous reference value.

This project borrows from a lot of other implementations to provide a pythonic, batteries included snapshot testing solution. It also tries to feel as native to [`pytest`](https://docs.pytest.org/en/stable/) as possible with its integrated review tool.

### Features

- Expressive and familiar assertion syntax
- Can format text, binary, hexdump, json and pickle snapshots out-of-the-box
- Can be extended with custom snapshot formats
- Interactive review tool for inspecting and approving changes

### Credits

- [`insta`](https://github.com/mitsuhiko/insta) (rust)

  Armin's work was the initial motivation for this project and inspired the reviewing workflow.

- [`jest`](https://jestjs.io/docs/en/snapshot-testing) (javascript)

  Jest enabled the mass adoption of snapshot testing throughout the JavaScript ecosystem and now basically stands as the reference when it comes to what snapshot testing is supposed to look like.

## Installation

The package can be installed with `pip`.

```bash
$ pip install pytest-insta
```

## Getting Started

The `snapshot` fixture is a function that returns the current value of a snapshot.

```python
def test_hello_world(snapshot):
    assert snapshot() == "hello"
```

```bash
$ pytest
...
CREATE snapshots/<prefix>__hello_world__0.txt
```

Running this test will create a new text file in the `snapshots` directory. The next time pytest runs, the test will load the snapshot and compare it to the actual value.

The return value of the `snapshot` function can be assigned to a variable and used multiple times.

```python
def test_hello_world(snapshot):
    expected = snapshot()
    assert expected == "hello"
    assert expected.upper() == "HELLO"
```

By default, each invocation of the `snapshot` function will generate its own snapshot.

```python
def test_hello_world(snapshot):
    assert snapshot() == "hello"
    assert snapshot() == "world"
```

```bash
$ pytest
...
CREATE snapshots/<prefix>__hello_world__0.txt
CREATE snapshots/<prefix>__hello_world__1.txt
```

You can also name snapshots explicitly. This makes it possible to load a snapshot multiple times during the same test.

```python
def test_hello_world(snapshot):
    assert snapshot("message.txt") == "hello"
    assert snapshot("message.txt") == "hello"
```

```bash
$ pytest
...
CREATE snapshots/<prefix>__hello_world__message.txt
```

## Snapshot Formats

By default, the `snapshot` fixture will store snapshots as `.txt` files. By providing a filename or just a specific file extension, you can create snapshots using various formats supported out-of-the-box.

```python
def test_hello_world(snapshot):
    assert snapshot("json") == {"hello": "world"}
    assert snapshot("expected.json") == {"hello": "world"}
```

```bash
$ pytest
...
CREATE snapshots/<prefix>__hello_world__0.json
CREATE snapshots/<prefix>__hello_world__expected.json
```

Note that the plugin doesn't diff the snapshot files themselves but actually loads snapshots back into the interpreter and performs comparisons on live python objects. This makes it possible to use snapshot formats that aren't directly human-readable like pure binary files and pickle.

| Built-in Formats | Extension  | Supported Types                              |
| ---------------- | ---------- | -------------------------------------------- |
| Plain text       | `.txt`     | `str`                                        |
| Binary           | `.bin`     | `bytes`                                      |
| Hexdump          | `.hexdump` | `bytes`                                      |
| Json             | `.json`    | Any object serializable by the json module   |
| Pickle           | `.pickle`  | Any object serializable by the pickle module |

The built-in formats should get you covered most of the time but you can also really easily implement your own snapshot formats.

```python
from dataclasses import dataclass
from pathlib import Path

from pytest_insta import Fmt

@dataclass
class Point:
    x: int
    y: int

class FmtPoint(Fmt[Point]):
    extension = ".pt"

    def load(self, path: Path) -> Point:
        return Point(*map(int, path.read_text().split()))

    def dump(self, path: Path, value: Point):
        path.write_text(f"{value.x} {value.y}")

def test_hello_world(snapshot):
    assert snapshot("pt") == Point(4, 2)
```

You can create a custom formatter by inheriting from the `Fmt` class and defining custom `load` and `dump` methods. The `extension` attribute associates the custom formatter to the specified file extension.

Custom formatters can be defined anywhere in your test suite but it's recommended to keep them in `conftest.py` if they're meant to be used across multiple files.

## Command-line Options

The plugin extends the `pytest` cli with a new `--insta` option that accommodates the snapshot-testing workflow. The option can be set to one of the following strategies:

- `update` - Record and update differing snapshots
- `update-new` - Record and create snapshots that don't already exist
- `update-none` - Don't record or update anything
- `record` - Record and save differing snapshots to be reviewed later
- `review` - Record and save differing snapshots then bring up the review tool
- `review-only` - Don't run tests and only bring up the review tool
- `clear` - Don't run tests and clear all the snapshots to review

If the option is not specified, the strategy will default to `update-none` if `pytest` is running in a CI environment and `update-new` otherwise. This makes sure that your pipeline properly catches any snapshot you might forget to push while keeping the development experience seamless by automatically creating snapshots as you're writing tests.

The `record` option is useful if you're in the middle of something and your snapshots keep changing. Differing snapshots won't cause tests to fail and will instead be recorded and saved.

```bash
$ pytest --insta record
...
RECORD .pytest_cache/d/insta/<prefix>__hello_world__0.txt

NOTICE 1 snapshot to review
```

When you're done making changes you can use the `review` option to bring up the review tool after running your tests. Each differing snapshot will display a diff and let you inspect the new value and the old value in a python repl.

```bash
$ pytest --insta review
...
_____________________________ [1/1] _____________________________

old: snapshots/example_hello_world__0.txt
new: .pytest_cache/d/insta/example_hello_world__0.txt

>       assert old == new
E       assert 'hello' == 'world'
E         - world
E         + hello

test_example.py:1: test_hello_world

a: accept, r: reject, s: skip
>>>
```

Finally, the `update` option will let you update any differing snapshot according to the current test run, without going through the review tool.

```bash
$ pytest --insta update
...
UPDATE snapshots/<prefix>__hello_world__0.txt
```

It's worth mentioning that the updating, recording and reviewing strategies take into account any filter you might specify with the `-k` or `-m` options.

## Caveats

The `snapshot` fixture hijacks equality checks to record changes. This keeps assertions expressive and readable but introduces two caveats that you need to be aware of.

- **Right-sided snapshots ❌**

  If an object's `__eq__` method doesn't return `NotImplemented` when its type doesn't match the compared object, the snapshot won't be able to record the updated value if it's placed on the right side of the comparison.

  <details>
  <summary>
  Explanation
  </summary>

  ***

  Strings return `NotImplemented` when compared to non-string objects so the following test will behave as expected.

  ```python
  def test_bad(snapshot):
      assert "hello" == snapshot()  # This works
  ```

  However, dataclasses return `False` when compared to objects of different types and won't let the snapshot record any changes when placed on the left-side of the comparison.

  ```python
  from dataclasses import dataclass
  from pathlib import Path

  from pytest_insta import Fmt

  @dataclass
  class Point:
      x: int
      y: int

  class FmtPoint(Fmt[Point]):
      extension = ".pt"

      def load(self, path: Path) -> Point:
          return Point(*map(int, path.read_text().split()))

      def dump(self, path: Path, value: Point):
          path.write_text(f"{value.x} {value.y}")

  def test_bad(snapshot):
      assert Point(4, 2) == snapshot("pt")  # This doesn't work
  ```

  </details>

  **Recommendation ✅**

  To avoid confusion and keep things consistent, always put snapshots on the left-side of the comparison.

  ```python
  def test_good(snapshot):
      assert snapshot() == "hello"
  ```

  ```python
  def test_good(snapshot):
      assert snapshot("pt") == Point(4, 2)
  ```

- **Not comparing snapshots ❌**

  Snapshots should first be compared to their actual value before being used in other expressions and assertions.

  <details>
  <summary>
  Explanation
  </summary>

  ***

  The comparison records the current value if the snapshot doesn't exist yet. In the following example, the test will fail before the actual comparison and the snapshot will not be generated.

  ```python
  def test_bad(snapshot):
      expected = snapshot()
      assert expected.upper() == "HELLO"  # This doesn't work
      assert expected == "hello"
  ```

  ```bash
  $ pytest
  ...
  >       assert expected.upper() == "HELLO"
  E       AttributeError: 'SnapshotNotfound' object has no attribute 'upper'
  ```

  </details>

  **Recommendation ✅**

  Always compare the snapshot to its actual value first and only perform additional operations afterwards.

  ```python
  def test_good(snapshot):
      expected = snapshot()
      assert expected == "hello"
      assert expected.upper() == "HELLO"
  ```

## Contributing

Contributions are welcome. Make sure to first open an issue discussing the problem or the new feature before creating a pull request. The project uses [`poetry`](https://python-poetry.org).

```bash
$ poetry install
```

You can run the tests with `poetry run pytest`.

```bash
$ poetry run pytest
```

The project must type-check with [`pyright`](https://github.com/microsoft/pyright). If you're using VSCode the [`pylance`](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) extension should report diagnostics automatically. You can also install the type-checker locally with `npm install` and run it from the command-line.

```bash
$ npm run watch
$ npm run check
```

The code follows the [`black`](https://github.com/psf/black) code style. Import statements are sorted with [`isort`](https://pycqa.github.io/isort/).

```bash
$ poetry run isort pytest_insta tests
$ poetry run black pytest_insta tests
$ poetry run black --check pytest_insta tests
```

---

License - [MIT](https://github.com/vberlier/pytest-insta/blob/master/LICENSE)
