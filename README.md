# pytest-insta

> A flexible and user-friendly snapshot testing plugin for pytest.

```python
assert snapshot() == "awesome!"
```

## Introduction

Snapshot testing makes it easy to monitor and approve changes by comparing the result of an operation against a previous reference value.

This project borrows from a lot of other implementations but reinterprets what it means to work with snapshots in an expressive language like Python. It also tries to feel as native to [`pytest`](https://docs.pytest.org/en/stable/) as possible with its integrated reviewing tool.

### Features

- Expressive and familiar assertion syntax
- Named and unnamed snapshots
- Handles text, binary, hexdump, json and pickle snapshots out-of-the-box
- The plugin can be extended with custom snapshot formats
- Integrated reviewing tool with live repl for inspecting the new value and the old value

### Credits

- [`insta`](https://github.com/mitsuhiko/insta) (rust)

  Armin's work was the initial inspiration for this project and shaped the reviewing workflow. The name was cool too. 😎

- [`jest`](https://jestjs.io/docs/en/snapshot-testing) (javascript)

  Jest enabled the mass-adoption of snapshot testing throughout the JavaScript ecosystem and now basically stands as the reference when it comes to what snapshot testing is supposed to look like.

## Installation

The package can be installed with `pip`.

```bash
$ pip install pytest-insta
```

## Contributing

Contributions are welcome. This project uses [`poetry`](https://python-poetry.org).

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
