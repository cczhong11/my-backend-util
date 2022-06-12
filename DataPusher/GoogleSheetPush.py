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

    def clean_data(self, items=None):
        data = []
        if self.topic == "sheet_clean_hahaha":

            for line in self.all_data:
                if line[2] == "让自己开心一点":
                    continue
                if len(line[0]) == 0:
                    continue
                data.append(line)
        if self.topic == "sheet_clean_tag":
            links = set()
            if not isinstance(items, dict):
                return
            for tag, olinks in items.items():
                for l in olinks:
                    links.add(l)

            for line in self.all_data:
                if line[3] in links:
                    continue
                if len(line[0]) == 0:
                    continue
                data.append(line)
        if self.debug:
            print(data)
            return
        self.sheet.clear()
        self.sheet.update("A1", data)

    def get_tags(self):
        rs = {}
        for line in self.all_data:
            if len(line[0]) == 0 or len(line[4]) == 0:
                continue
            if line[4] not in rs:
                rs[line[4]] = []
            rs[line[4]].append(line[3])  # use link
        return rs

    def health_check(self):
        return True
