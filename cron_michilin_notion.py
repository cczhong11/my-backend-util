from DataFetcher.MichelinDataFetcher import MichelinDataFetcher
from DataFetcher.YelpDataFetcher import YelpDataFetcher
from DataPusher.NotionPush import NotionPush, notion_util

from web_util import read_json_file
from constant import PATH
from log_util import logger
import urllib
import sys

params = {"aroundLatLngViaIP": "true",
          "aroundRadius": "all",
          "filters": 'status:Published AND sites:california',
          "hitsPerPage": 100,
          "attributesToRetrieve": ["_geoloc", "region", "city", "cuisines", "good_menu", "image", "main_image", "michelin_award", "name", "slug", "new_table", "offers", "offers_size", "online_booking", "other_urls", "site_name", "take_away", "url"],
          "maxValuesPerFacet": 200,
          "page": 0,
          "facets": ["country.cname", "country.slug", "region.slug", "city.slug", "good_menu", "new_table", "take_away", "distinction.slug", "green_star.slug", "offers", "cuisines.slug", "area_slug", "online_booking", "facilities.slug", "categories.lvl0"], "tagFilters": ""}

def get_post_data(new_params):
    p = urllib.parse.urlencode(new_params)
    data = {"requests":[{"indexName":"prod-restaurants-en","params":p}]}
    data = str(data)
    data = data.replace("'","\"")
    data = data.replace("'","\"")   
    data = data.replace("%27","%22")
    return data

def run():
    # health_check
    api = read_json_file(f"{PATH}/key.json")
    michelin = MichelinDataFetcher(f"{PATH}/cookie/michelin.cookie", '')
    notion_push = NotionPush(api['notion_key'])
    yelp = YelpDataFetcher(api['yelp_api'],'')
    if not michelin.health_check() or not yelp.health_check():
        logger.exception("micheline health check failed")
        sys.exit(1)
    
    # get data
    rs = []
    for page in range(4):
        params["page"] = page
        data = get_post_data(params)
        r = michelin.get_data(data)
        rs.extend(r)
    
    current_data = notion_push.get_current_data("michelin")
    for r in rs:
        if r.name not in current_data:
            continue
        #notion_push.push_data(r,'michelin')
        if current_data[r.name][1] != -1:
            continue
        result = yelp.get_data(r.name, f"{r.city}, {r.region}")
        if len(result) > 0:
            r.yelp_link = f"https://www.yelp.com/biz/{result[0]['alias']}"
            r.yelp_rating = result[0]['rating']
            r.price = result[0].get("price","UNKNOWN")
        else:
            continue
        logger.info(f"{r.name} updated")
        notion_push.update_page(current_data[r.name][0],properties={"yelp_rating":notion_util(r.yelp_rating, 'number'), "yelp_link":notion_util(r.yelp_link, 'url'), 'price':notion_util(r.price, 'select')})
if __name__ == '__main__':
    run()