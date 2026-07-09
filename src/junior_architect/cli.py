"""`junior-architect` command-line entry point: a REPL chat with the agent."""
import argparse
import logging
import sys

from .agent import JuniorArchitectAgent
from .backend.fake_backend import FakeBackend
from .backend.logging_backend import LoggingBackend


def build_backend(name: str, verbose: bool = False, dry_run: bool = False):
    if name == "fake":
        backend = FakeBackend()
    elif name == "autocad":
        from .backend.win32_backend import Win32ComBackend

        backend = Win32ComBackend()
    else:
        raise ValueError(f"Unknown backend '{name}'")

    # dry_run implies logging (there'd be nothing to observe otherwise).
    if verbose or dry_run:
        backend = LoggingBackend(backend, dry_run=dry_run)
    return backend


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
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Log every AutoCAD operation the agent performs.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log operations without executing them (implies --verbose). Preview a plan without drawing.",
    )
    args = parser.parse_args(argv)

    if args.verbose or args.dry_run:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        backend = build_backend(args.backend, verbose=args.verbose, dry_run=args.dry_run)
    except (RuntimeError, ValueError) as exc:
        print(f"Could not start backend: {exc}", file=sys.stderr)
        return 1

    agent = JuniorArchitectAgent(backend, model=args.model)

    banner = "Junior Architect ready. Describe what to draft (Ctrl-D to quit)."
    if args.dry_run:
        banner += " [dry-run: operations are logged, not executed]"
    print(banner)
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
