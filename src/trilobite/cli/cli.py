from __future__ import annotations

import argparse
from trilobite.config.config import AppConfig, CFGAnalysis, CFGDataBase, CFGDev, CFGMisc, CFGTickerService
from trilobite.cli.runtimeflags import CliFlags

def parse_args(argv: list[str]) -> tuple[AppConfig, CliFlags]:
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
    p.add_argument("--top-n", type=int, help="Top N tickers to display")
    p.add_argument("--n-factors", type=int, help="Components for PCA extraction")
    #p.add_argument("--min-days", type=int, help="Minimum trading days required in DB")
    p.add_argument("--lookback", type=int, help="Lookback window (days)")
    p.add_argument("--horizon", type=int, help="Prediction horizon (days)")
    p.add_argument("--epochs", type=int, help="Training epochs")
    p.add_argument("--period", type=str, help="Period to use, e.g. '30d', '2w', '4m', '6y'")
    p.add_argument("--ticker", type=str, help="Ticker to use")

    p.add_argument("--display-graph", action="store_true", help="Displays a graph of '--ticker' adjusted close over '--period'")
    p.add_argument("--updateall", action="store_true", help="Updates all tickers to today")
    p.add_argument("--train-nn", action="store_true", help="Train NN and print ranked predictioN")


    ns = p.parse_args(argv)
    #config
    def _use_cli_or_cfg(cli_arg, cfg_arg):
        """
        """
        return cli_arg if cli_arg is not None else cfg_arg

    dev = CFGDev(
        dev = _use_cli_or_cfg(ns.dev, CFGDev.dev),
        debug = _use_cli_or_cfg(ns.debug, CFGDev.debug) or _use_cli_or_cfg(ns.dev, CFGDev.dev),
        dry_run = _use_cli_or_cfg(ns.dry_run, CFGDev.dry_run),
        consolelog = _use_cli_or_cfg(ns.consolelog, CFGDev.consolelog),
    )
    tickerservice = CFGTickerService(
        default_date = _use_cli_or_cfg(ns.default_date, CFGTickerService.default_date),
        default_timedelta = _use_cli_or_cfg(ns.default_timedelta, CFGTickerService.default_timedelta),
    )
    #Might need to create flags for these two later
    db = CFGDataBase()
    misc = CFGMisc()
    analysis = CFGAnalysis(
        top_n = _use_cli_or_cfg(ns.top_n, CFGAnalysis.top_n),
        n_factors = _use_cli_or_cfg(ns.n_factors, CFGAnalysis.n_factors),
        lookback = _use_cli_or_cfg(ns.lookback, CFGAnalysis.lookback),
        horizon = _use_cli_or_cfg(ns.horizon, CFGAnalysis.horizon),
        epochs = _use_cli_or_cfg(ns.epochs, CFGAnalysis.epochs),
        period = _use_cli_or_cfg(ns.period, CFGAnalysis.period),
        ticker = _use_cli_or_cfg(ns.ticker, CFGAnalysis.ticker),
    )
    cfg = AppConfig(
        dev=dev,
        ticker=tickerservice,
        db=db,
        misc=misc,
        analysis=analysis,
    )
    #Cliflags
    cliflags = CliFlags(
        updateall=ns.updateall,
        train_nn=ns.train_nn,
        display_graph=ns.display_graph
    )
    return cfg, cliflags


