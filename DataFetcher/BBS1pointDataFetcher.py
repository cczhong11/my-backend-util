import requests
from bs4 import BeautifulSoup
from .DataFetcherBase import DataFetcherBase
from web_util import parse_curl
import re
INTERVAL = "分钟"
PATTERN = {
    "job": r'<u><b><font color=\"green\">(.*?)</font><font color=\"#00B2E8\">(.*?)</font></b>@<b><font color=\"#FF6600\">(.*?)</font></b></u>.*<b>\[<font color=\"purple\">(.*?)</font>@<font color=\"brown\">(.*?)</font>\] (.*)</b>(.*)\n',
    "application": r'<font color=\"#666\">(.*?)</font>.<font color=\"blue\">(.*?)</font>.<font color=\"black\"><b>(.*?)</b>\]</font>\[<font color=\"#F60\"><b>(.*?)</b></font>@<font color=\"#00B2E8\">(.*?)</font>\]</u> - <font color=\"brown\">(.*?)</font> - <font color=\"green\">(.*?)</font><font color=\"purple\">(.*?)</font>,<font color=\"hotpink\">.*</font><font color=\"brown\">.*</font>'
}

HEALTHCHECKURL = {
    'job': "https://www.1point3acres.com/bbs/forum.php?mod=forumdisplay&fid=145&filter=author&orderby=dateline&sortid=311",
    'application':"https://www.1point3acres.com/bbs/forum.php?mod=forumdisplay&fid=82&filter=author&orderby=dateline&sortid=164"
}

class BBS1pointDataFetcher(DataFetcherBase):
    def __init__(self, cookie, topic, run_feq="1h",enable=True):
        self.topic = topic
        self.header = {}
        self.feedList = []
        super(BBS1pointDataFetcher, self).__init__(cookie, run_feq, enable)
    
    def load_cookie(self):
        cookie_str = ""
        with open(self.cookie) as f:
            cookie_str = f.read()
        _,header = parse_curl(cookie_str)
        self.header = header
    
    def get_data(self, url=""):
        feedRes = []
        for idx,feed in enumerate(self.feedList):
            rs = feed.findAll("a", {"class": "s xst"})
            feedTitle = rs[0]
            feedUrl = feedTitle.attrs["href"]
            feedTitle = feedTitle.text
            
            if feed.findChild("td", attrs={"class": "by"}) is None or INTERVAL not in feed.findChild("td", attrs={"class": "by"}).text:
                continue
            result = re.findall(PATTERN[self.topic], str(feed))
            if len(result) == 0:
                continue
            if self.topic == "job":
                jobname, jobtype,company,result, roundname,edu,exp = result[0]
                reStr = f"{feedTitle}\nhttps://www.1point3acres.com/bbs/{feedUrl} #{company} {jobname}@{jobtype} {roundname} {exp} "
            elif self.topic == "application": 
                semester,level,ad,track,school,_,_,_ = result[0]
                reStr = f"{feedTitle}\nhttps://www.1point3acres.com/bbs/{feedUrl} 录取汇报 {semester}.{level}.{ad} {track}@ #{school}"
            feedRes.append(reStr)
        return feedRes
        
     
    def health_check(self):
        result = requests.get(HEALTHCHECKURL[self.topic], headers=self.header).content
        soup = BeautifulSoup(result, "lxml")
        self.feedList = soup.findAll("tbody",id=lambda x: x and x.startswith('normalthread_'))

        if len(self.feedList) == 0:
            #print(self.header)
            #print(soup)
            print("no feed list")
            return False
        feed = self.feedList[0]
        feed_title = feed.findAll("a", {"class": "s xst"})
        if len(feed_title) != 1:
            print("no feed title")
            return False
        result = re.findall(PATTERN[self.topic], str(feed))
        if len(result) != 1:
            print("regex wrong")
            return False
        return True


