from .DataFetcherBase import DataFetcherBase
import requests
import datetime
import json

yesterday = datetime.datetime.now() - datetime.timedelta(days=1)


url = "https://gql.jdbinvesting.com/gqlrealanon"

headers = {
    "authority": "gql.jdbinvesting.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    "authorization": "Bearer",
    "content-type": "application/json",
    "origin": "https://www.jdbinvesting.com",
    "referer": "https://www.jdbinvesting.com/",
    "sec-ch-ua": '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
}

data = {
    "operationName": "Query",
    "variables": {"ytVideoSumListBId": "ALL"},
    "query": """fragment YtVideoSumBInfo on YTVideoSummaryB {
  id
  title
  sumList
  avatarUrl
  ytChanTitle
  link
  videoID
  publishedAt
  reaction
  numLike
  numDislike
  __typename
}

query Query($ytVideoSumListBId: String!) {
  ytVideoSumListB(id: $ytVideoSumListBId) {
    id
    ytVidSumList {
      ...YtVideoSumBInfo
      __typename
    }
    __typename
  }
}""",
}


class JiudianArticleFetcher(DataFetcherBase):
    def __init__(self):
        self.result = None

    def get_data(self):
        # Assuming response_json is the JSON object you got from the request
        rs = []
        try:
            yt_video_sum_list_b = self.result["data"]["ytVideoSumListB"]["ytVidSumList"]

            for video in yt_video_sum_list_b:
                published_at = video.get("publishedAt", "N/A")
                try:
                    published_at = int(published_at) / 1000
                    if published_at < yesterday.timestamp():
                        continue
                except Exception as e:
                    print(e)
                    pass
                sum_list = video.get("sumList", "N/A")

                title = video.get("title", "N/A")
                yt_chan_title = video.get("ytChanTitle", "N/A")
                extracted_texts = []
                sum_list_json = json.loads(sum_list)
                for item in sum_list_json[0]["children"]:
                    text = item["children"][0].get("text", "N/A")
                    extracted_texts.append(text)

                rs.append(
                    {
                        "title": title,
                        "yt_chan_title": yt_chan_title,
                        "extracted_texts": extracted_texts,
                        "published_at": published_at,
                    }
                )
        except:
            print("The keys you are looking for are not in the response. 😢")
        return rs

    def health_check(self):
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            self.result = response.json()
            return True
        return False
