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

This project borrows from a lot of other implementations to provide a pythonic, batteries included snapshot testing solution. It also tries to feel as native to [`pytest`](https://docs.pytest.org/en/stable/) as possible with its integrated reviewing tool.

### Features

- Expressive and familiar assertion syntax
- Can format text, binary, hexdump, json and pickle snapshots out-of-the-box
- The plugin can be extended with custom snapshot formats
- Interactive reviewing tool for inspecting and approving changes

### Credits

- [`insta`](https://github.com/mitsuhiko/insta) (rust)

  Armin's work was the initial motivation for this project. It inspired the reviewing workflow by keeping everything as straightforward as possible. The name was pretty cool too.

- [`jest`](https://jestjs.io/docs/en/snapshot-testing) (javascript)

  Jest enabled the mass adoption of snapshot testing throughout the JavaScript ecosystem and now basically stands as the reference when it comes to what snapshot testing is supposed to look like.

## Installation

The package can be installed with `pip`.

```bash
$ pip install pytest-insta
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
