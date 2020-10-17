# pytest-insta

[![Build Status](https://travis-ci.com/vberlier/pytest-insta.svg?branch=main)](https://travis-ci.com/vberlier/pytest-insta)
[![PyPI](https://img.shields.io/pypi/v/pytest-insta.svg)](https://pypi.org/project/pytest-insta/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pytest-insta.svg)](https://pypi.org/project/pytest-insta/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

<img align="right" width="50%" src="https://raw.githubusercontent.com/vberlier/pytest-insta/main/demo.svg?sanitize=true">

> A user-friendly snapshot testing plugin for pytest.

```python
assert snapshot() == "awesome!"
```

## Introduction

Snapshot testing makes it easy to monitor and approve changes by comparing the result of an operation against a previous reference value.

This project borrows from a lot of other implementations to provide a pythonic, batteries included snapshot testing solution. It also tries to feel as native to [`pytest`](https://docs.pytest.org/en/stable/) as possible with its integrated review tool.

### Features

- Expressive and familiar assertion syntax
- Can format text, binary, hexdump, json and pickle snapshots out-of-the-box
- The plugin can be extended with custom snapshot formats
- Interactive review tool for inspecting and approving changes

### Credits

- [`insta`](https://github.com/mitsuhiko/insta) (rust)

  Armin's work was the initial motivation for this project. It inspired the review workflow by keeping everything as straightforward as possible. The name was pretty cool too.

- [`jest`](https://jestjs.io/docs/en/snapshot-testing) (javascript)

  Jest enabled the mass adoption of snapshot testing throughout the JavaScript ecosystem and now basically stands as the reference when it comes to what snapshot testing is supposed to look like.

## Installation

The package can be installed with `pip`.

```bash
$ pip install pytest-insta
```

## Getting started

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

Running this test will create a new snapshot in the `snapshots` directory. The next time pytest runs, the test will load the snapshot and compare it to the actual value.

> **Note**
>
> You shouldn't add the `snapshots` directory to your `.gitignore`. Snapshots are supposed to be checked into source control.

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
    assert snapshot("message.txt") == "HELLO".lower()
```

```bash
$ pytest
...
CREATE snapshots/<prefix>__hello_world__message.txt
```

## Snapshot formats

> **WIP**

## Command-line options

> **WIP**

## Review tool

> **WIP**

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

The project must type-check with [`mypy`](http://mypy-lang.org) and [`pylint`](https://www.pylint.org) shouldn't report any error.

```bash
$ poetry run mypy
$ poetry run pylint pytest_insta tests
```

The code follows the [`black`](https://github.com/psf/black) code style. Import statements are sorted with [`isort`](https://pycqa.github.io/isort/).

```bash
$ poetry run isort pytest_insta tests
$ poetry run black pytest_insta tests
$ poetry run black --check pytest_insta tests
```

---

License - [MIT](https://github.com/vberlier/pytest-insta/blob/master/LICENSE)
