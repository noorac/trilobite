from __future__ import annotations

from dataclasses import dataclass
import time

from tqdm import tqdm

from trilobite.commands.uicommands import (
    CmdNotAnOption, 
    CmdQuit, 
    CmdUpdateAll,
    Command, 
)
from trilobite.events.uievents import (
    EvtExit,
    EvtStartUp,
    EvtStatus, 
    EvtProgress,
    Event, 
)

class CLIController:
    def __init__(self, argv: list[str]) -> None:
        self._argv = argv
        self._bar = None

    def get_command(self) -> Command:
        """
        Decides which command to send to Handler
        """
        if "--updateall" in self._argv:
            self._argv = [e for e in self._argv if e != "--updateall"]
            return CmdUpdateAll()
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

