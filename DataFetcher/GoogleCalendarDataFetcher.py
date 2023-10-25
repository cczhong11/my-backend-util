# fetch google calendar data automatically

from typing import Iterable
from .DataFetcherBase import DataFetcherBase
from gcsa.google_calendar import GoogleCalendar
from gcsa.event import Event


class GoogleCalendarDataFetcher(DataFetcherBase):
    def __init__(self, secret_file, credentials_file, run_feq="1h", enable=True):
        self.header = {}
        self.feedList = []
        self.query = ""
        self.service = None
        self.credentials_file = credentials_file
        self.secret_file = secret_file
        super(GoogleCalendarDataFetcher, self).__init__("", run_feq, enable)

    def load_cookie(self):
        self.gc = GoogleCalendar(credentials_path=self.credentials_file)

    def get_data(self, calendar_id, time_min=None, time_max=None) -> Iterable[Event]:
        return self.gc.get_events(
            time_min=time_min, time_max=time_max, calendar_id=calendar_id
        )

    def health_check(self):
        return True
