from     datetime                                          import datetime

class Shift:

    def __init__(
        self,
        p_id: int | None,
        p_project: str,
        p_schedule_id: str,
        p_analyst_name: str,
        p_start: datetime,
        p_end: datetime
    ):
        self.id = p_id
        self.project = p_project
        self.schedule_id = p_schedule_id
        self.analyst_name = p_analyst_name
        self.start = p_start
        self.end = p_end
