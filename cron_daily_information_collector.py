from DataFetcher.GMailDataFetcher import GMailDataFetcher, NewsLetterType
from DataFetcher.GoogleCalendarDataFetcher import GoogleCalendarDataFetcher
from web_util import read_json_file
from DataWriter.OpenAIDataWriter import OpenAIDataWriter
from constant import PATH
import time_util
import dataclasses
import re
from web_util import read_json_file


@dataclasses.dataclass
class DailyInformation:
    events: list
    wsj_news: str


life_calendar = "ingv5kmgh4k3t5g0vrqc6lhsgg@group.calendar.google.com"
today = time_util.str_time(time_util.get_current_date(), "%Y/%m/%d")
yesterday = time_util.str_time(time_util.get_yesterday(), "%Y/%m/%d")
api = read_json_file(f"{PATH}/key.json")


def clean_wsj(content):
    cleaned_content = re.sub(r"â\x80\x8c\s*", "", content)
    lines = cleaned_content.split("\n")

    # Keeping lines that contain alphanumeric characters
    readable_lines = [line for line in lines if re.search(r"\w", line)]

    new_lines = []
    for line in readable_lines:
        if "Email us your comments, which we may edit" in line:
            break
        new_lines.append(line)
    readable_content = "\n".join(new_lines)
    return readable_content


def run_calendar():
    cal = GoogleCalendarDataFetcher(
        secret_file=None, credentials_file=f"{PATH}/cookie/gmailcredentials.json"
    )
    cal.load_cookie()
    events = cal.get_data(
        life_calendar, time_util.get_current_date(), time_util.get_next_day()
    )
    return events


def run_wsj():
    gmail = GMailDataFetcher(
        f"{PATH}/cookie/gmail.json", f"{PATH}/cookie/gmailcredentials.json"
    )
    if not gmail.health_check():
        raise Exception("gmail health check failed")
    gmail.reset_query()
    gmail.set_sender(NewsLetterType.WSJ)
    gmail.set_time(yesterday, today)
    tmp = gmail.get_data()
    rs = gmail.analyze(NewsLetterType.WSJ, tmp)
    wsj = rs[0]["content"]
    wsj = clean_wsj(wsj)
    openai = OpenAIDataWriter(api["openai"])
    wsj_summary = openai.summary_data(
        "这是一段10条新闻。最后说说在那些方面的股票可能会受到上述新闻的影响。", wsj, use_16k_model=True
    )
    return wsj_summary


def run():
    events = run_calendar()
    wsj_summary = run_wsj()
    print(wsj_summary)


if __name__ == "__main__":
    run()
