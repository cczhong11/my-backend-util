from .DataFetcherBase import DataFetcherBase
import requests

place = {"nanjing": 105570, "sunnyvale": 331979}


class AccuweatherDataFetcher(DataFetcherBase):
    def __init__(self, cookie, address, run_feq="1h", enable=True):
        super().__init__(cookie, run_feq, enable)
        self.address = address

    def get_data(self):
        name = self.address.lower()
        rs = requests.post(
            f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{place[name]}?apikey={self.cookie}&language=zh-cn&metric=true"
        ).json()

        return f"{name}: {rs['Headline']['Text']}\n温度 {rs['DailyForecasts'][0]['Temperature']['Minimum']['Value']} - {rs['DailyForecasts'][0]['Temperature']['Maximum']['Value']}"
