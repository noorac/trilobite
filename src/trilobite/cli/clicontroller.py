from __future__ import annotations

from dataclasses import dataclass
import time

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

    def get_command(self) -> Command:
        """
        Decides which command to send to Handler
        """
        if "--updateall" in self._argv:
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
                print(f"{evt.label} {evt.current}/{evt.total}")
                time.sleep(evt.waittime)

