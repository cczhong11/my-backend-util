from .DataPusherBase import DataPusherBase
import gspread
from log_util import logger


class GoogleSheetPush(DataPusherBase):
    def __init__(self, filename, sheet, topic, filter, debug=False):
        self.gc = gspread.service_account(filename)
        self.sheet = self.gc.open_by_key(sheet).sheet1
        self.all_data = self.sheet.get_all_values()
        self.current_line = len(self.all_data) + 1
        self.topic = topic
        self.filter = filter
        self.debug = debug

    def push_data(self, data):
        if self.debug:
            print(f"send: {data}")
            return {}
        if self.topic == "money":
            money_type = self.filter.filter(data[1])
            self.sheet.update(
                f"A{self.current_line}:D{self.current_line}",
                [[data[2], data[1], float(data[0]), money_type]],
            )
            self.current_line += 1
        logger.info(f"send: {data}")
        return {"result": "success"}

    def clean_data(self):

        if self.topic == "sheet_clean_hahaha":
            data = []
            for line in self.all_data:
                if line[2] == "让自己开心一点":
                    continue
                data.append(line)
        if self.debug:
            print(data)
            return
        self.sheet.clear()
        self.sheet.update("A2", data)

    def health_check(self):
        return True
