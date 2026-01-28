from __future__ import annotations

import argparse
from trilobite.cli.runtimeflags import RuntimeFlags
from trilobite.cli.cliflags import CLIFlags

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
    p.add_argument("--consolelog", action="store_true", help="Logging will output to the console")
    p.add_argument("--train-nn", action="store_true", help="Train NN and print ranked predictioN")
    p.add_argument("--topn", type=int, default=20, help="Top N tickers to display")
    p.add_argument("--n-factors", type=int, default=20, help="Components for PCA extraction")
    p.add_argument("--min-days", type=int, default=1260, help="Minimum trading days required in DB")
    p.add_argument("--lookback", type=int, default=60, help="Lookback window (days)")
    p.add_argument("--horizon", type=int, default=1, help="Prediction horizon (days)")
    p.add_argument("--epochs", type=int, default=10, help="Training epochs")


    ns = p.parse_args(argv)

    runtimeflags = RuntimeFlags(
        dev = ns.dev,
        debug=ns.debug or ns.dev,
        dry_run=ns.dry_run,
        curses=ns.curses,
        consolelog=ns.consolelog,
    )
    cliflags = CLIFlags(
        updateall=ns.updateall,
        train_nn=ns.train_nn,
        topn=ns.topn,
        n_factors=ns.n_factors,
        min_days=ns.min_days,
        lookback=ns.lookback,
        horizon=ns.horizon,
        epochs=ns.epochs,
    )
    return runtimeflags,cliflags, ns


