from dataclasses import dataclass

class Event: ...

@dataclass(frozen=True)
class EvtStatus(Event):
    text: str
    waittime: int = 0

@dataclass(frozen=True)
class EvtProgress(Event):
    label: str
    current: int
    total: int
    waittime: int = 0

@dataclass(frozen=True)
class EvtStartUp(Event): ...


