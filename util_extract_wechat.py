from DataExtractor.WechatExtractor import WechatExtractor
from constant import PATH


def main():
    wechat = WechatExtractor(f"{PATH}/cookie/wechat.cookie")
    rs = wechat.extract_data("https://mp.weixin.qq.com/s/vV6jR_gOfPgj8zjn4rhmsw")
    print(rs)


if __name__ == "__main__":
    main()
