from __future__ import annotations

from dataclasses import dataclass
import time

from tqdm import tqdm

from trilobite.cli.runtimeflags import RuntimeFlags
from trilobite.cli.cliflags import CLIFlags
from trilobite.commands.uicommands import (
    CmdNotAnOption, 
    CmdQuit,
    CmdTrainNN, 
    CmdUpdateAll,
    Command, 
)
from trilobite.events.uievents import (
    EvtExit,
    EvtPredictionRanked,
    EvtStartUp,
    EvtStatus, 
    EvtProgress,
    Event, 
)

class CLIController:
    def __init__(self, flags: CLIFlags) -> None:
        self._flags = flags
        self._bar = None

    def get_command(self) -> Command:
        """
        Decides which command to send to Handler
        """
        if self._flags.updateall:
            #self._argv = [e for e in self._argv if e != "--updateall"]
            self._flags.updateall = False
            return CmdUpdateAll()
        if self._flags.train_nn:
            self._flags.train_nn = False
            return CmdTrainNN(self._flags.topn)
        else:
            return CmdQuit()

    def handle_event(self, evt: Event) -> None:
        """
        Handles events returned from Handler
        """
        match evt:
            case EvtStatus():
                print(f"{evt.text}")
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
                print(f"{evt.date}:\n{evt.ranked}")
                

