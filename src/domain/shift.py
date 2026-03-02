from     datetime                                          import datetime

class Shift:

    def __init__(
        self,
        p_id: int | None,
        p_analyst_id: int,
        p_project: str,
        p_schedule_id: str,
        p_start_time: str,
        p_end_time: str
    ):
        self.id = p_id
        self.analyst_id = p_analyst_id
        self.project = p_project
        self.schedule_id = p_schedule_id
        self.start_time = p_start_time
        self.end_time = p_end_time