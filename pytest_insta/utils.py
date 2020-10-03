__all__ = ["normalize_node_name", "hexdump", "hexload", "is_ci"]


import math
import os
import re


def normalize_node_name(name: str):
    return re.sub(
        r"\W+", "_", re.sub(r"^(tests?[_/])*|([_/]tests?)*(\.\w+)?$", "", name)
    ).strip("_")


def hexdump(data: bytes, n: int = 16):
    for k, i in enumerate(range((len(data) + n - 1) // n)):
        values = data[i * n : (i + 1) * n]
        line = values.hex(b" ", -2)
        suffix = "".join(chr(i) if chr(i).isprintable() else "." for i in values)
        yield f"{k * n:08x}:  {line:{math.ceil(n * 2.5)}} {suffix}"


def hexload(dump: str):
    return b"".join(bytes.fromhex(line.split("  ")[1]) for line in dump.splitlines())


def is_ci():
    return "CI" in os.environ or "TF_BUILD" in os.environ
