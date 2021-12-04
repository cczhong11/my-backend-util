# load people's weibo and save to md
import requests
import traceback
import json
import os
import random
import re
import sys
import traceback
from collections import OrderedDict
from datetime import date, datetime, timedelta
from time import sleep
from lxml import etree
from requests.adapters import HTTPAdapter
from tqdm import tqdm
import requests
from .DataFetcherBase import DataFetcherBase
from pathlib import Path

PATH = os.path.join(str(Path.home()), "data")
# save in ~/data
user_id_list = [
    "5780439194",
]  # ["2163127221"]#["2810373291", "1974576991","2286908003", "1652811601"]
user_map = {
    "2810373291": "新华网",
    "1974576991": "环球时报",
    "2286908003": "人民网",
    "1652811601": "喷嚏",
    "2163127221": "LZ",
    "1799869881": "me",
    "5780439194": "表情包",
    "5700379397": "bqb",
}


class WeiboDataFetcher(DataFetcherBase):
    def __init__(self, cookie, enable=True):
        self.wb = WeiboSpider(cookie, user_id_list)
        self.data = []
        super(WeiboDataFetcher, self).__init__(enable=enable)

    def load_cookie(self):
        pass

    def get_data(self):
        try:
            self.wb.start()  # 爬取微博信息
            filepath = self.wb.get_filepath("md")
            return filepath
        except ValueError:
            print(
                "config.json 格式不正确，请参考 " "https://github.com/dataabc/weiboSpider#3程序设置"
            )
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()
            return

    def health_check(self):
        return True


class WeiboSpider(object):
    def __init__(self, cookie, new_user_id_list):
        self.cookie = {"Cookie": cookie}
        self.filter = 0
        self.user_id = 123
        self.weibo_id_list = []
        self.got_num = 0
        self.downlaod_bqb = True
        nowtime = datetime.now()  # datetime.strptime(config['since_date'],"%Y-%m-%d")
        self.since_date = nowtime - timedelta(days=4)
        self.end_date = datetime(
            nowtime.year, nowtime.month, nowtime.day
        )  # self.since_date+timedelta(days=1)#datetime.strptime(config['end_date'],"%Y-%m-%d")
        self.date_str = f"{self.since_date.strftime('%Y_%m_%d')}_{self.end_date.strftime('%Y_%m_%d')}"
        self.user_id_list = new_user_id_list
        self.weibo = []  # 存储爬取到的所有微博信息

    def deal_html(self, url):
        try:
            html = requests.get(url, cookies=self.cookie).content

            selector = etree.HTML(html)
            return selector
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def extract_picture_urls(self, info, weibo_id):
        """提取微博原始图片url"""
        try:
            a_list = info.xpath("div/a/@href")
            first_pic = "https://weibo.cn/mblog/pic/" + weibo_id + "?rl=0"
            all_pic = "https://weibo.cn/mblog/picAll/" + weibo_id + "?rl=1"
            if first_pic in a_list:
                if all_pic in a_list:
                    selector = self.deal_html(all_pic)
                    preview_picture_list = selector.xpath("//img/@src")
                    picture_list = [
                        p.replace("/thumb180/", "/large/") for p in preview_picture_list
                    ]
                    picture_urls = ",".join(picture_list)
                else:
                    if info.xpath(".//img/@src"):
                        preview_picture = info.xpath(".//img/@src")[-1]
                        picture_urls = preview_picture.replace("/wap180/", "/large/")
                    else:
                        sys.exit(
                            "爬虫微博可能被设置成了'不显示图片'，请前往"
                            "'https://weibo.cn/account/customize/pic'，修改为'显示'"
                        )
            else:
                picture_urls = "无"
            return picture_urls
        except Exception as e:
            return "无"
            print("Error: ", e)
            traceback.print_exc()

    def get_page_num(self, selector):
        """获取微博总页数"""
        try:
            if selector.xpath("//input[@name='mp']") == []:
                page_num = 1
            else:
                page_num = (int)(
                    selector.xpath("//input[@name='mp']")[0].attrib["value"]
                )
            return page_num
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_filepath(self, type):
        """获取结果文件路径"""
        try:
            file_dir = PATH + os.sep + "weibo" + os.sep
            if type == "img" or type == "video":
                file_dir = file_dir + os.sep + type
            if not os.path.isdir(file_dir):
                os.makedirs(file_dir)
            if type == "img" or type == "video":
                return file_dir
            file_path = (
                file_dir
                + os.sep
                + user_map[self.user_id]
                + "_"
                + self.date_str
                + "."
                + type
            )
            print(file_path)
            return file_path
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_picture_urls(self, info, is_original):
        """获取微博原始图片url"""
        try:
            weibo_id = info.xpath("@id")[0][2:]
            picture_urls = {}
            if is_original:
                original_pictures = self.extract_picture_urls(info, weibo_id)
                picture_urls["original_pictures"] = original_pictures
                if True:
                    picture_urls["retweet_pictures"] = "无"
            else:
                retweet_url = info.xpath("div/a[@class='cc']/@href")[0]
                retweet_id = retweet_url.split("/")[-1].split("?")[0]
                retweet_pictures = self.extract_picture_urls(info, retweet_id)
                picture_urls["retweet_pictures"] = retweet_pictures
                a_list = info.xpath("div[last()]/a/@href")
                original_picture = "无"
                for a in a_list:
                    if a.endswith((".gif", ".jpeg", ".jpg", ".png")):
                        original_picture = a
                        break
                picture_urls["original_pictures"] = original_picture
            return picture_urls
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_video_url(self, info, is_original):
        """获取微博视频url"""
        try:
            if is_original:
                div_first = info.xpath("div")[0]
                a_list = div_first.xpath(".//a")
                video_link = "无"
                for a in a_list:
                    if "m.weibo.cn/s/video/show?object_id=" in a.xpath("@href")[0]:
                        video_link = a.xpath("@href")[0]
                        break
                if video_link != "无":
                    video_link = video_link.replace(
                        "m.weibo.cn/s/video/show", "m.weibo.cn/s/video/object"
                    )
                    wb_info = requests.get(video_link, cookies=self.cookie).json()
                    video_url = wb_info["data"]["object"]["stream"].get("hd_url")
                    if not video_url:
                        video_url = wb_info["data"]["object"]["stream"]["url"]
                        if not video_url:  # 说明该视频为直播
                            video_url = "无"
            else:
                video_url = "无"
            return video_url
        except Exception as e:
            return "无"
            print("Error: ", e)
            traceback.print_exc()

    def is_original(self, info):
        """判断微博是否为原创微博"""
        is_original = info.xpath("div/span[@class='cmt']")
        if len(is_original) > 3:
            return False
        else:
            return True

    def deal_garbled(self, info):
        """处理乱码"""
        try:
            info = (
                info.xpath("string(.)")
                .replace("\u200b", "")
                .encode(sys.stdout.encoding, "ignore")
                .decode(sys.stdout.encoding)
            )
            return info
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_long_weibo(self, weibo_link):
        """获取长原创微博"""
        try:
            selector = self.deal_html(weibo_link)
            info = selector.xpath("//div[@class='c']")[1]
            wb_content = self.deal_garbled(info)
            wb_time = info.xpath("//span[@class='ct']/text()")[0]
            weibo_content = wb_content[
                wb_content.find(":") + 1 : wb_content.rfind(wb_time)
            ]
            return weibo_content
        except Exception as e:
            return "网络出错"
            print("Error: ", e)
            traceback.print_exc()

    def get_long_retweet(self, weibo_link):
        """获取长转发微博"""
        try:
            wb_content = self.get_long_weibo(weibo_link)
            weibo_content = wb_content[: wb_content.rfind("原文转发")]
            return weibo_content
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_original_weibo(self, info, weibo_id):
        """获取原创微博"""
        try:
            weibo_content = self.deal_garbled(info)
            weibo_content = weibo_content[: weibo_content.rfind("赞")]
            a_text = info.xpath("div//a/text()")
            if "全文" in a_text:
                weibo_link = "https://weibo.cn/comment/" + weibo_id
                wb_content = self.get_long_weibo(weibo_link)
                if wb_content:
                    weibo_content = wb_content
            return weibo_content
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_retweet(self, info, weibo_id):
        """获取转发微博"""
        try:
            original_user = info.xpath("div/span[@class='cmt']/a/text()")
            if not original_user:
                wb_content = "转发微博已被删除"
                return wb_content
            else:
                original_user = original_user[0]
            wb_content = self.deal_garbled(info)
            wb_content = wb_content[wb_content.find(":") + 1 : wb_content.rfind("赞")]
            wb_content = wb_content[: wb_content.rfind("赞")]
            a_text = info.xpath("div//a/text()")
            if "全文" in a_text:
                weibo_link = "https://weibo.cn/comment/" + weibo_id
                weibo_content = self.get_long_retweet(weibo_link)
                if weibo_content:
                    wb_content = weibo_content
            retweet_reason = self.deal_garbled(info.xpath("div")[-1])
            retweet_reason = retweet_reason[: retweet_reason.rindex("赞")]
            wb_content = (
                "\n\n - "
                + retweet_reason
                + "\n"
                + "- 原始用户: "
                + original_user
                + "\n"
                + "- 转发内容: "
                + wb_content
            )
            return wb_content
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_weibo_content(self, info, is_original):
        """获取微博内容"""
        try:
            weibo_id = info.xpath("@id")[0][2:]
            if is_original:
                weibo_content = self.get_original_weibo(info, weibo_id)
            else:
                weibo_content = self.get_retweet(info, weibo_id)
            return weibo_content
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def is_pinned_weibo(self, info):
        """判断微博是否为置顶微博"""
        kt = info.xpath(".//span[@class='kt']/text()")
        if kt and kt[0] == "置顶":
            return True
        else:
            return False

    def get_publish_time(self, info):
        """获取微博发布时间"""
        try:
            str_time = info.xpath("div/span[@class='ct']")
            str_time = self.deal_garbled(str_time[0])
            publish_time = str_time.split("来自")[0]
            if "刚刚" in publish_time:
                publish_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            elif "分钟" in publish_time:
                minute = publish_time[: publish_time.find("分钟")]
                minute = timedelta(minutes=int(minute))
                publish_time = (datetime.now() - minute).strftime("%Y-%m-%d %H:%M")
            elif "今天" in publish_time:
                today = datetime.now().strftime("%Y-%m-%d")
                time = publish_time[3:]
                publish_time = today + " " + time
                if len(publish_time) > 16:
                    publish_time = publish_time[:16]
            elif "月" in publish_time:
                year = datetime.now().strftime("%Y")
                month = publish_time[0:2]
                day = publish_time[3:5]
                time = publish_time[7:12]
                publish_time = year + "-" + month + "-" + day + " " + time
            else:
                publish_time = publish_time[:16]
            return publish_time
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_weibo_footer(self, info):
        """获取微博点赞数、转发数、评论数"""
        try:
            footer = {}
            pattern = r"\d+"
            str_footer = info.xpath("div")[-1]
            str_footer = self.deal_garbled(str_footer)
            str_footer = str_footer[str_footer.rfind("赞") :]
            weibo_footer = re.findall(pattern, str_footer, re.M)

            up_num = int(weibo_footer[0])
            footer["up_num"] = up_num

            retweet_num = int(weibo_footer[1])
            footer["retweet_num"] = retweet_num

            comment_num = int(weibo_footer[2])
            footer["comment_num"] = comment_num
            return footer
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_one_weibo(self, info):
        """获取一条微博的全部信息"""
        try:
            weibo = OrderedDict()
            is_original = self.is_original(info)
            if True or is_original:
                weibo["id"] = info.xpath("@id")[0][2:]
                weibo["content"] = self.get_weibo_content(info, is_original)  # 微博内容
                picture_urls = self.get_picture_urls(info, is_original)
                weibo["original_pictures"] = picture_urls[
                    "original_pictures"
                ]  # 原创图片url
                if not self.filter:
                    weibo["retweet_pictures"] = picture_urls[
                        "retweet_pictures"
                    ]  # 转发图片url
                    weibo["original"] = is_original  # 是否原创微博
                weibo["video_url"] = self.get_video_url(info, is_original)  # 微博视频url
                weibo["publish_time"] = self.get_publish_time(info)  # 微博发布时间
                footer = self.get_weibo_footer(info)
                weibo["up_num"] = footer["up_num"]  # 微博点赞数
                weibo["retweet_num"] = footer["retweet_num"]  # 转发数
                weibo["comment_num"] = footer["comment_num"]  # 评论数
            else:
                weibo = None
            return weibo
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def get_one_page(self, page):
        """获取第page页的全部微博"""
        try:
            url = "https://weibo.cn/u/%s?page=%d" % (self.user_id, page)
            selector = self.deal_html(url)
            info = selector.xpath("//div[@class='c']")
            is_exist = info[0].xpath("div/span[@class='ctt']")
            if is_exist:
                for i in range(0, len(info) - 2):
                    weibo = self.get_one_weibo(info[i])
                    if weibo:
                        if weibo["id"] in self.weibo_id_list:
                            continue
                        publish_time = datetime.strptime(
                            weibo["publish_time"][:10], "%Y-%m-%d"
                        )

                        if publish_time < self.since_date:
                            if self.is_pinned_weibo(info[i]):
                                continue
                            else:
                                return True
                        if publish_time >= self.end_date:
                            continue
                        self.weibo.append(weibo)
                        self.weibo_id_list.append(weibo["id"])
                        self.got_num += 1
                        print("-" * 100)
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def write_md(self, wrote_num):
        """将爬取的信息写入txt文件"""
        try:
            temp_result = []
            if wrote_num == 0:
                if self.filter:
                    result_header = "\n\n原创微博内容: \n"
                else:
                    result_header = "\n\n微博内容: \n"

                temp_result.append(result_header)
            for i, w in enumerate(self.weibo[wrote_num:]):
                photo = [f"- ![]({p})" for p in w["original_pictures"].split(",")]
                retweet_pictures = [
                    f"- ![]({p})" for p in w["retweet_pictures"].split(",")
                ]
                temp_result.append(
                    str(wrote_num + i + 1)
                    + ":"
                    + "https://weibo.cn/comment/"
                    + w["id"]
                    + "\n\n"
                    + w["content"]
                    + "\n"
                    + "\n".join(photo)
                    + "\n"
                    + "\n".join(retweet_pictures)
                    + "\n"
                    + "- 发布时间: "
                    + w["publish_time"]
                    + "\n"
                    + "点赞数: "
                    + str(w["up_num"])
                    + "   转发数: "
                    + str(w["retweet_num"])
                    + "   评论数: "
                    + str(w["comment_num"])
                    + "\n\n"
                )
            result = "".join(temp_result)
            with open(self.get_filepath("md"), "ab") as f:
                f.write(result.encode(sys.stdout.encoding))
            print("%d条微博写入txt文件完毕,保存路径:" % self.got_num)
            print(self.get_filepath("md"))
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def write_data(self, wrote_num):
        """将爬取到的信息写入文件或数据库"""
        if self.got_num > wrote_num:
            self.write_md(wrote_num)
            # self.weibo_to_sqlite(wrote_num)

    def get_weibo_info(self):
        """获取微博信息"""
        try:
            url = "https://weibo.cn/u/%s" % (self.user_id)
            selector = self.deal_html(url)

            page_num = self.get_page_num(selector)  # 获取微博总页数
            wrote_num = 0
            page1 = 0
            random_pages = random.randint(1, 5)
            print(page_num)
            for page in tqdm(range(1, page_num + 1), desc="Progress"):
                is_end = self.get_one_page(page)  # 获取第page页的全部微博
                if is_end:
                    break

                if page > 0:  # 每爬20页写入一次文件
                    self.write_data(wrote_num)
                    wrote_num = self.got_num

                # 通过加入随机等待避免被限制。爬虫速度过快容易被系统限制(一段时间后限
                # 制会自动解除)，加入随机等待模拟人的操作，可降低被系统限制的风险。默
                # 认是每爬取1到5页随机等待6到10秒，如果仍然被限，可适当增加sleep时间
                if page - page1 == random_pages and page < page_num:
                    sleep(random.randint(6, 10))
                    page1 = page
                    random_pages = random.randint(1, 5)

            self.write_data(wrote_num)  # 将剩余不足20页的微博写入文件
            if not self.filter:
                print("共爬取" + str(self.got_num) + "条微博")
            else:
                print("共爬取" + str(self.got_num) + "条原创微博")
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def initialize_info(self, user_id):
        """初始化爬虫信息"""
        self.got_num = 0
        self.weibo = []
        self.user = {}
        self.user_id = user_id
        self.weibo_id_list = []

    def start(self):
        """运行爬虫"""
        try:
            for user_id in self.user_id_list:
                self.initialize_info(user_id)
                print("*" * 100)
                self.get_weibo_info()
                print("信息抓取完毕")
                print("*" * 100)

        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()
