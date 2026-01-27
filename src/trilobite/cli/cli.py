from __future__ import annotations

import argparse
from trilobite.cli.runtimeflags import CLIFlags, RuntimeFlags

def parse_args(argv: list[str]) -> tuple[RuntimeFlags,CLIFlags, argparse.Namespace]:
    """
    Parses over the arguments to create runtimeflags that can be used in
    the program
    """
    p = argparse.ArgumentParser(prog = "trilobite")
    p.add_argument("--dev", action="store_true", help="Enable developer conviniences")
    p.add_argument("--debug", action="store_true", help="Enable debug logging")
    p.add_argument("--dry-run", action="store_true", help="Do not write to DB")
    p.add_argument("--curses", action="store_true", help="Uses curses for UI")
    p.add_argument("--updateall", action="store_true", help="Uses curses for UI")

    ns = p.parse_args(argv)

    runtimeflags = RuntimeFlags(
        dev = ns.dev,
        debug=ns.debug or ns.dev,
        dry_run=ns.dry_run,
        curses=ns.curses,
    )
    cliflags = CLIFlags(
        updateall=ns.updateall,
    )
    return runtimeflags,cliflags, ns


