
from dataclasses import dataclass

@dataclass(frozen=True)
class CmdQuit:
    pass
@dataclass(frozen=True)
class CmdUpdateAll: 
    pass
Command = (
    CmdQuit |
    CmdUpdateAll
)
