from bs4 import BeautifulSoup
from .DataExtractorBase import DataExtractorBase
import requests
import re


class WechatExtractor(DataExtractorBase):
    def __init__(self, cookie: str):
        super().__init__()
        with open(cookie) as f:
            self.cookie = f.read().strip()
        # self.cookie = cookie

    def get_info(self, url):
        payload = {}

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cookie": self.cookie,
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "TE": "trailers",
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        return response.text

    def get_first(self, info, reStart, reEnd):
        regex = r"" + reStart + "(.*?)" + reEnd
        pat = re.compile(regex, re.S)
        content = re.findall(pat, info)
        return content[0]

    def get_detail(self, url):
        info = self.get_info(url)
        soup = BeautifulSoup(info, "html.parser")
        title = soup.find_all("meta", {"property": "og:title"}, limit=1)[0].get(
            "content"
        )
        info = self.get_first(
            info, '<div class="rich_media_content', '<script type="text/javascript"'
        )
        info = '<div class="rich_media_content' + info
        info = info.replace("</strong>", "\n").replace("</span>", "\n")
        pattern = re.compile(r"<[^>]+>", re.S)
        result = pattern.sub("", str(info))
        return result, title

    def extract_data(self, url):
        rs = self.get_detail(url)
        return rs
