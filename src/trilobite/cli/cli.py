from __future__ import annotations

import argparse
from trilobite.cli.runtimeflags import CliFlags, ConfigFlags

def parse_args(argv: list[str]) -> tuple[ConfigFlags, CliFlags]:
    """
    Parses over the arguments to create runtimeflags that can be used in
    the program
    """
    p = argparse.ArgumentParser(prog = "trilobite")
    p.add_argument("--dev", action="store_true", help="Enable developer conviniences")
    p.add_argument("--debug", action="store_true", help="Enable debug logging")
    p.add_argument("--dry-run", action="store_true", help="Do not write to DB")
    p.add_argument("--consolelog", action="store_true", help="Logging will output to the console")
    p.add_argument("--default-date", type=str, help="Default date, format 'YYYY-MM-DD'")
    p.add_argument("--default-timedelta", type=int, help="Default how many days of overlap when updating")
    p.add_argument("--topn", type=int, help="Top N tickers to display")
    p.add_argument("--n-factors", type=int, help="Components for PCA extraction")
    p.add_argument("--min-days", type=int, help="Minimum trading days required in DB")
    p.add_argument("--lookback", type=int, help="Lookback window (days)")
    p.add_argument("--horizon", type=int, help="Prediction horizon (days)")
    p.add_argument("--epochs", type=int, help="Training epochs")

    p.add_argument("--updateall", action="store_true", help="Updates all tickers to today")
    p.add_argument("--train-nn", action="store_true", help="Train NN and print ranked predictioN")


    ns = p.parse_args(argv)

    configflags = ConfigFlags(
        dev = ns.dev,
        debug=ns.debug or ns.dev,
        dry_run=ns.dry_run,
        consolelog=ns.consolelog,
        default_date=ns.default_date,
        default_timedelta=ns.default_timedelta,
        topn=ns.topn,
        n_factors=ns.n_factors,
        min_days=ns.min_days,
        lookback=ns.lookback,
        horizon=ns.horizon,
        epochs=ns.epochs,
    )
    cliflags = CliFlags(
        updateall=ns.updateall,
        train_nn=ns.train_nn,
    )
    return configflags, cliflags


