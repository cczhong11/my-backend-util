from .DataReaderBase import DataReaderBase
import gspread


class GoogleSheetReader(DataReaderBase):
    def __init__(self, filename, sheet):
        self.gc = gspread.service_account(filename)
        self.sheet_id = sheet
        self.sheet = self.gc.open_by_key(sheet)
        self.all_data = self.sheet.sheet1.get_all_values()
        self.current_line = len(self.all_data) + 1
        super(GoogleSheetReader, self).__init__()

    def get_data(self, sheetname):

        return self.sheet.worksheet(sheetname).get_all_values()

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
