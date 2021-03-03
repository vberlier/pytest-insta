__all__ = ["ReviewTool"]


from code import InteractiveConsole
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Collection, Dict, Iterator, Optional, Tuple

from _pytest.terminal import TerminalReporter

from .format import Fmt
from .utils import node_path_name


class ReviewEnvironment(Dict[str, Any]):
    outcome: Optional[Tuple[str, str]] = None
    decisions = {
        "a": "accepting snapshot",
        "r": "rejecting snapshot",
        "s": "skipping snapshot",
    }

    def __getitem__(self, key: str) -> Any:
        if value := self.decisions.get(key):
            self.outcome = key, value
            return None
        return super().__getitem__(key)


class ReviewConsole(InteractiveConsole):
    def raw_input(self, prompt: str = "") -> str:
        if self.locals.outcome:  # type: ignore
            raise EOFError()
        return super().raw_input(prompt)


@dataclass
class ReviewTool:
    tr: TerminalReporter
    config: Any
    record_dir: Path
    tests: Collection[Any]

    @property
    def recorded_snapshots(self) -> Iterator[Tuple[Any, Path]]:
        for test in self.tests:
            path, name = node_path_name(test)
            for snapshot in (self.record_dir / path.parent).glob(f"{name}__*"):
                yield test, snapshot

    def display_assertion(self, old: Any, new: Any):
        self.tr.write_line("\n>       assert old == new")

        lines, *_ = self.config.hook.pytest_assertrepr_compare(
            config=self.config, op="==", left=old, right=new
        )

        explanation = "assert " + "\n".join("  " + line for line in lines).strip()

        for line in explanation.splitlines():
            self.tr.write_line(f"E       {line}", blue=True, bold=True)

    def collect(self) -> Iterator[Tuple[Path, Optional[Path]]]:
        if to_review := list(self.recorded_snapshots):
            self.tr.write_line("")
            self.tr.section("SNAPSHOT REVIEWS")

        for i, (test, recorded) in enumerate(to_review):
            original = (
                recorded.parent.relative_to(self.record_dir)
                / "snapshots"
                / recorded.name
            )

            self.tr.ensure_newline()
            self.tr.section(f"[{i + 1}/{len(to_review)}]", "_", blue=True, bold=True)

            self.tr.write_line(f"\nold: {original!s}")
            self.tr.write_line(f"new: {recorded!s}")

            if not (fmt := Fmt.from_spec(original.name)[1]):
                self.tr.write_line(
                    f"\ninvalid snapshot format: {original.name!r}", red=True, bold=True
                )
                continue

            old = fmt.load(original)
            new = fmt.load(recorded)

            self.display_assertion(old, new)

            module, line, name = test.location

            self.tr.write(f"\n{module}", blue=True, bold=True)
            self.tr.write_line(f":{line + 1}: {name}")

            decision, message = self.prompt(old, new)
            self.tr.write_line(message, bold=True)

            if decision == "a":
                yield recorded, original
            elif decision == "r":
                yield recorded, None

    def prompt(self, old: Any, new: Any) -> Tuple[str, str]:
        review_env = ReviewEnvironment(old=old, new=new)

        try:
            import readline
            import rlcompleter

            readline.set_completer(rlcompleter.Completer(review_env).complete)
            readline.parse_and_bind("tab: complete")
        except ImportError:
            pass

        console = ReviewConsole(review_env)
        console.interact("\na: accept, r: reject, s: skip", "")

        return review_env.outcome or ("s", "skipping snapshot")
