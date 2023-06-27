from DataReader.SqliteDBReader import SqliteDBReader
from DataPusher.NotionPush import NotionPush, notion_util
from web_util import read_json_file
from time_util import get_current_date, add_time, str_time
from constant import PATH
from log_util import logger
import sys
import os

logger.setLevel("INFO")
os_name = os.uname().nodename
config_path = "pi_indeed_path"
if "MacBook" in os_name:
    config_path = "mac_indeed_path"
now = get_current_date()
one_months_ago = add_time(now, days=-1.5 * 30)
six_months_ago = add_time(now, days=-6 * 30)
sqls = {
    "junior_swe": f"""
    select * from indeed where type = 'software engineer' and experience in ('1', '2', '0', 'new grad','intern', 'UNKNOWN','NO YEAR INFO') and (LOWER(title) like '%grad%' or LOWER(title) like '%entr%' or LOWER(title) like '%junior%'  or LOWER(title) like '% I %') and (LOWER(title) not like '%staff%') and date >= '{str_time(one_months_ago)}' order by date desc
    """,
    "interior design internship": f"select * from indeed where date >= '{str_time(six_months_ago)}' and type = 'interior design internship' order by date desc",
    "junior quantitative analyst": f"select * from indeed where date >= '{str_time(one_months_ago)}' and type = 'junior quantitative analyst' order by date desc",
}


def run():
    # health_check
    api = read_json_file(f"{PATH}/key.json")
    config = read_json_file(f"{PATH}/config.json")
    sqlite_reader = SqliteDBReader(
        config[config_path],
    )
    notion_push = NotionPush(api["notion_key"])
    if not sqlite_reader.health_check():
        logger.exception("sqlite health check failed")
        sys.exit(1)

    for topic, junior_sql in sqls.items():
        logger.info(f"topic: {topic}, sql: {junior_sql}")
        # get data
        current_data = notion_push.get_indeed_job(topic)
        logger.info(f"current data: {len(current_data)}")
        data = sqlite_reader.get_data(junior_sql)

        visited_job_id = set()
        visit_job = set()
        for row in data:
            job = {
                "job_id": row[0],
                "title": row[3],
                "company": row[2],
                "city": row[10],
                "posted": row[1],
                "state": row[11],
                "link": row[16],
            }
            name = row[3] + " " + row[2]
            if name in current_data:
                visit_job.add(name)
                continue

            if name in visit_job:
                continue
            visited_job_id.add(row[0])
            visit_job.add(name)
            logger.info("write job: " + str(job))
            notion_push.push_indeed_job(job, topic)

        for job_name in current_data:
            if job_name not in visit_job:
                logger.info("archived job: " + job_name)
                notion_push.update_page(current_data[job_name][0], archived=True)


if __name__ == "__main__":
    run()
