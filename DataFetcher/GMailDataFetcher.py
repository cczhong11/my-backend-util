import requests
from bs4 import BeautifulSoup
from .DataFetcherBase import DataFetcherBase
from oauth2client import file, client, tools
from httplib2 import Http
from enum import Enum
from googleapiclient.discovery import build
import re
from pathlib import Path
import base64
from log_util import logger
PATH = str(Path(__file__).parent.absolute())
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'


class EmailType(Enum):
    CHASE = 1
    DISCOVER = 2
    #AMEX = 3
    #VENMO = 4


class GMailDataFetcher(DataFetcherBase):
    def __init__(self, secret_file, credentials_file, run_feq="1h", enable=True):
        self.header = {}
        self.feedList = []
        self.query = ""
        self.service = None
        self.credentials_file = credentials_file
        self.secret_file = secret_file
        super(GMailDataFetcher, self).__init__("", run_feq, enable)

    def load_cookie(self):
        store = file.Storage(self.secret_file)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(
                self.credentials_file, SCOPES)
            creds = tools.run_flow(flow, store)
        self.service = build('gmail', 'v1', http=creds.authorize(Http()),cache_discovery=False)
        print("load successful")

    def get_data(self):
        messages = []
        try:
            logger.info(self.query)
            response = self.service.users().messages().list(userId='me',
                                                            q=self.query).execute()
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(userId='me',
                                                                q=self.query, pageToken=page_token).execute()
                messages.extend(response['messages'])
            print(len(messages))
            return messages
        except Exception as e:
            print(e)

    def set_sender(self, sender):
        mail = ""
        if sender == EmailType.CHASE:
            mail = "no.reply.alerts@chase.com"
        elif sender == EmailType.DISCOVER:
            mail = "discover@services.discover.com"
        self.query += f"from:({mail}) "

    def set_time(self, begin, end):
        self.query += f"after:{begin} before:{end} "

    def health_check(self):

        response = self.service.users().messages().list(userId='me',
                                                        q=self.query).execute()
        if 'messages' in response:
            return True
        return False

    def analyze(self, email_type, messages):
        result = []
        for m in messages:
            mess = self.service.users().messages().get(
                userId='me', id=m["id"]).execute()
            if email_type == EmailType.CHASE:
                result.append(self.analyze_chase(mess))
            if email_type == EmailType.DISCOVER:
                result.append(self.analyze_discover(mess))
        # filter none
        return result

    def analyze_discover(self, message):
        if "payload" not in message:
            return
        # decode base64 data
        if "parts" not in message["payload"]:
            data = [message["payload"]]
        else:
            data = message["payload"]["parts"]
        for p in data:
            data = p["body"]["data"]

            content = base64.urlsafe_b64decode(data).decode("ISO-8859-1")

            rs = re.findall(
                r"Transaction Date: (.*)<br/>[\d\D]+Merchant: (.*)<br/>[\d\D]+Amount: \$([.\d]+)", content)

            if len(rs) > 0:
                return (rs[0][2], rs[0][1], rs[0][0])
        return None

    def analyze_chase(self, message):
        if "payload" not in message:
            return
        # decode base64 data
        if "parts" not in message["payload"]:
            data = [message["payload"]]
        else:
            data = message["payload"]["parts"]
        for p in data:
            data = p["body"]["data"]

            content = base64.urlsafe_b64decode(data).decode("ISO-8859-1")
            date = ""
            Merchant = ""
            money = ""
            soup = BeautifulSoup(content, 'lxml')
            result = soup.findAll("td", attrs={"class": "font14"})
            for i, r in enumerate(result):
                if r.text == "Date":
                    date = result[i+1].text
                if r.text == "Merchant":
                    Merchant = result[i+1].text
                if r.text == "Amount":
                    money = result[i+1].text[1:]
            if Merchant == "":
                continue
            return (float(money), Merchant, date)
        return None

    def reset_query(self):
        self.query = ""
