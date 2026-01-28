
from dataclasses import dataclass

class Command: ...

@dataclass(frozen=True)
class CmdQuit(Command): ...

@dataclass(frozen=True)
class CmdUpdateAll(Command): ...

@dataclass(frozen=True)
class CmdNotAnOption(Command): ...

@dataclass(frozen=True)
class CmdTrainNN(Command):
    top_n: int = 20

