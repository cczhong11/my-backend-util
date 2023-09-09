import random

from bs4 import BeautifulSoup
from DataFetcher.AccuweatherDataFetcher import AccuweatherDataFetcher
from DataFetcher.GMailDataFetcher import GMailDataFetcher, NewsLetterType
from DataFetcher.GoogleCalendarDataFetcher import GoogleCalendarDataFetcher
from DataFetcher.RSSDataFetcher import RSSDataFetcher
from DataReader.PersonalBackendReader import PersonalBackendReader
from DataFetcher.ZhihuArticleFetcher import ZhihuArticleFetcher
from DataWriter.OpenAIDataWriter import OpenAIDataWriter
from constant import PATH
import time_util
import dataclasses
import re
from web_util import read_json_file, parse_curl
import os


@dataclasses.dataclass
class BookWisdom:
    book_name: str
    wisdoms: list


@dataclasses.dataclass
class DailyInformation:
    events: list
    wsj_news: str
    weather: str
    hacker_news: list
    book_text: BookWisdom
    meitou: list


today = time_util.str_time(time_util.get_current_date(), "%Y/%m/%d")
yesterday = time_util.str_time(time_util.get_yesterday(), "%Y/%m/%d")
tomorrow = time_util.str_time(time_util.get_next_day(), "%Y/%m/%d")
api = read_json_file(f"{PATH}/key.json")
life_calendar = api["life_calendar"]
personal_backend_url = api["personal_backend_url"]
openai = OpenAIDataWriter(api["openai"])


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
    gmail.set_time(today, tomorrow)
    tmp = gmail.get_data()
    rs = gmail.analyze(NewsLetterType.WSJ, tmp)
    wsj = rs[0]["content"]
    wsj = clean_wsj(wsj)

    wsj_summary = openai.summary_data(
        "这是一段10条新闻。先说新闻，最后说说在那些方面的股票可能会受到上述新闻的影响。", wsj[:5000], use_16k_model=False
    )
    return wsj_summary


def run_weather():
    weather = AccuweatherDataFetcher(api["accuweather"], "sunnyvale")
    return weather.get_data()


def run_hacker_news():
    rss = RSSDataFetcher("https://hnrss.org/newest?points=500")
    news = rss.fetch(time_util.get_yesterday())
    return [n["title"] for n in news]


def run_book_wisdom():
    books = PersonalBackendReader(personal_backend_url)
    # choose a book
    random_book = random.choice(books.get_list("kindle")["data"])
    book_name = random_book["name"].split(".")[0]
    book_text = books.get_data("kindle", book_name)
    random_five = random.sample(book_text["data"][0]["data"].get("content"), 5)
    return BookWisdom(book_name, random_five)


def run_zhihu_meitou():
    with open(os.path.join(PATH, "cookie", "zhihu.cookie")) as f:
        cookie_str = f.read()
    url, header = parse_curl(cookie_str)
    result = ZhihuArticleFetcher(url, header).get_data()
    summary = []
    for article in result:
        c = article["content"]
        soup = BeautifulSoup(c, "html.parser")
        text = soup.get_text()
        if len(text) > 2000:
            text = text[:2000]
        summary.append(
            openai.summary_data("这是一段文章。总结一下里面的重要内容:", text, use_16k_model=False)
        )
    return summary


def run():
    events = run_calendar()
    wsj_summary = run_wsj()
    weather = run_weather()
    hacker_news = run_hacker_news()
    bookwisdom = run_book_wisdom()
    meitou = run_zhihu_meitou()
    daily_info = DailyInformation(
        events, wsj_summary, weather, hacker_news, bookwisdom, meitou
    )
    print(daily_info)


if __name__ == "__main__":
    run()
