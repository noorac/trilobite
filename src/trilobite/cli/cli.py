from __future__ import annotations

import argparse
from trilobite.cli.runtimeflags import CliFlags, ConfigFlags
from trilobite.config.models import AppConfig, CFGAnalysis, CFGDataBase, CFGDev, CFGMisc, CFGTickerService

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
    dev = CFGDev(
        dev = ns.dev,
        debug=ns.debug or ns.dev,
        dry_run=ns.dry_run,
        consolelog=ns.consolelog,
    )
    tickerservice = CFGTickerService(
        default_date=ns.default_date,
        default_timedelta=ns.default_timedelta,
    )
    db = CFGDataBase()
    misc = CFGMisc()
    analysis = CFGAnalysis(
        top_n=ns.topn,
        n_factors=ns.n_factors,
        lookback=ns.lookback,
        horizon=ns.horizon,
        epochs=ns.epochs,
        period=ns.period,
        ticker=ns.ticker,
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


