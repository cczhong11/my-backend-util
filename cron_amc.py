from DataFetcher.AMCMovieDataFetcher import AMCMovieDataFetcher
from web_util import read_json_file
from constant import PATH
from log_util import logger
def run():
    # health_check
    api = read_json_file(f"{PATH}/key.json")
    amc = AMCMovieDataFetcher(api['amc_key'])
    if not amc.health_check():
        logger.exception("amc health check failed")
    
    # get data
    data = amc.get_data("")
    print(data)

if __name__ == '__main__':
    run()