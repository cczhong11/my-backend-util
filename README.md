# 解决的问题

1. 定时爬取信息
2. 存储、读取我的信息
3. 推送信息


## 爬取信息


- datafetcher
  - fetch function
  - when (daily or request based)
  - logging
  - health check
- output
  - sql
  - log
  - txt
  - png
  - s3

## 存储、读取我的信息

- data I generate
  - markdown based on json
  - markdown free style
- data from the datafetcher
- data from other website
- data from static files


- datafetcher (request based)
- datareader
  - path
  - json template
- datawriter
  - path
  - method


## push data

- data from datafetcher
- data from static file
- push channel
  - wx
  - slack
  - telegram

- pusher
  - path
  - method


# Road map

1. update 1point3acres fetcher and telegram push
2. update personal dashboard
3. update read infra
4. update wx channel