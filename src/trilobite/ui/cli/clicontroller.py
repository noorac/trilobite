from __future__ import annotations

from dataclasses import dataclass
import time
import logging

from tqdm import tqdm

from trilobite.cli.runtimeflags import CliFlags
from trilobite.commands.uicommands import (
    CmdDisplayGraph,
    CmdNotAnOption, 
    CmdQuit,
    CmdTrainNN, 
    CmdUpdateAll,
    Command, 
)
from trilobite.config.config import CFGAnalysis
from trilobite.events.uievents import (
    EvtExit,
    EvtPredictionRanked,
    EvtStartUp,
    EvtStatus, 
    EvtProgress,
    Event, 
)

logger = logging.getLogger(__name__)

class CLIController:
    def __init__(self, flags: CliFlags) -> None:
        self._flags = flags
        self._bar = None

    def get_command(self) -> Command:
        """
        Decides which command to send to Handler
        """
        if self._flags.updateall:
            self._flags.updateall = False
            return CmdUpdateAll()
        if self._flags.train_nn:
            self._flags.train_nn = False
            return CmdTrainNN()
        if self._flags.display_graph:
            self._flags.display_graph = False
            return CmdDisplayGraph()
        else:
            return CmdQuit()

    def handle_event(self, evt: Event) -> None:
        """
        Handles events returned from Handler
        """
        match evt:
            case EvtStatus():
                logger.info(f"{evt.text}")
                time.sleep(evt.waittime)
            case EvtProgress():
                if self._bar is None:
                    self._bar = tqdm(total=evt.total, desc="Updating tickers")

                delta = evt.current - self._bar.n
                if delta > 0:
                    self._bar.update(delta)

                self._bar.set_postfix_str(evt.label)
                if evt.current == evt.total:
                    self._bar.close()
                    self._bar = None
                time.sleep(evt.waittime)
            case EvtPredictionRanked():
                logger.info(f"\nTop {evt.topn}: \n{evt.date}:\n{evt.ranked}")
                

