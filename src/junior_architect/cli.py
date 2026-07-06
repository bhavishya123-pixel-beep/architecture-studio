"""`junior-architect` command-line entry point: a REPL chat with the agent."""
import argparse
import sys

from .agent import JuniorArchitectAgent
from .backend.fake_backend import FakeBackend


def build_backend(name: str):
    if name == "fake":
        return FakeBackend()
    if name == "autocad":
        from .backend.win32_backend import Win32ComBackend

        return Win32ComBackend()
    raise ValueError(f"Unknown backend '{name}'")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="junior-architect",
        description="Chat with an AI junior architect that drafts in AutoCAD.",
    )
    parser.add_argument(
        "--backend",
        choices=["autocad", "fake"],
        default="autocad",
        help=(
            "'autocad' drives a live AutoCAD session over COM (Windows only); "
            "'fake' uses an in-memory drawing for testing/demo without AutoCAD."
        ),
    )
    parser.add_argument("--model", default="claude-sonnet-5", help="Claude model to use")
    args = parser.parse_args(argv)

    try:
        backend = build_backend(args.backend)
    except (RuntimeError, ValueError) as exc:
        print(f"Could not start backend: {exc}", file=sys.stderr)
        return 1

    agent = JuniorArchitectAgent(backend, model=args.model)

    print("Junior Architect ready. Describe what to draft (Ctrl-D to quit).")
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line.strip():
            continue
        try:
            reply = agent.send(line)
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            continue
        print(reply)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
