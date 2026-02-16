from   dataclasses                     import dataclass


@dataclass
class IncidentAnalyst:
    id                                 : int | None
    name                               : str
    email                              : str
