import requests
from bs4 import BeautifulSoup
from .DataFetcherBase import DataFetcherBase
from google.oauth2 import service_account
from google.cloud import texttospeech

from gne import GeneralNewsExtractor
import logging
import os

MAX_LETTER = 200
logger = logging.getLogger(__name__)
FFMPEG = "/usr/bin/ffmpeg"  # "/opt/homebrew/bin/ffmpeg"
gne = GeneralNewsExtractor()


class Article:
    def __init__(self, url):
        self.url = url
        self.title = None
        self.content = None
        self.publish_time = None
        self.delimeter = "_"

    def read_from_url(self, path):

        r = requests.get(self.url)
        rs = gne.extract(r.text, body_xpath='//div[@class="rich_media_area_primary"]')
        try:
            self.title = rs["title"]
            self.publish_time = rs["publish_time"]
            self.content = rs["content"]
        except:
            logger.error("Error in reading from url: {}".format(self.url))
        nline = len(self.content.split("\n"))
        print(f"there are {nline} lines")
        with open(os.path.join(path, f"{self.title}.txt"), "w") as f:
            f.write(self.content)

    def to_tts(self, tts, path):
        index = 0
        tmp = ""
        for line in self.content.split("\n"):
            if len(line.strip()) == 0:
                continue
            tmp += line
            if len(tmp) > MAX_LETTER:
                tts(tmp, "zh-CN", f"{self.title}{self.delimeter}{index}.mp3")
                tmp = ""
                index += 1
        tts(tmp, "zh-CN", f"{self.title}{self.delimeter}{index}.mp3")
        index += 1
        tmp_file = f"{self.title}.tmp.txt"
        new_file = f"{self.title}.mp3"
        with open(os.path.join(path, tmp_file), "w") as f:
            for i in range(index):
                f.write(f"file {path}/{self.title}{self.delimeter}{i}.mp3\n")
        cmd = f"{FFMPEG} -f concat -safe 0 -i {os.path.join(path, tmp_file)} -c copy {os.path.join(path, new_file)} "
        rs = os.system(cmd)
        if rs != 0:
            return
        for i in range(index):
            os.remove(os.path.join(path, f"{self.title}{self.delimeter}{i}.mp3"))


class TTSFetcher(DataFetcherBase):
    def __init__(self, cookie, path, enable=True):

        self.path = path
        self.client = None
        self.title = None
        super(TTSFetcher, self).__init__(cookie)

    def load_cookie(self):
        credentials = service_account.Credentials.from_service_account_file(self.cookie)
        self.client = texttospeech.TextToSpeechClient(credentials=credentials)
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

    def current_title(self):
        return self.title

    def get_data(self, url):
        article = Article(url)
        article.read_from_url(self.path)
        self.title = article.title
        if os.path.exists(os.path.join(self.path, f"{article.title}.mp3")):
            return
        article.to_tts(self.gTTS_text, self.path)

    def gTTS_text(self, text, lang, filename):
        if os.path.exists(os.path.join(self.path, filename)):
            return

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang,
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
            name="cmn-CN-Wavenet-A",
        )
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=self.audio_config
        )
        # The response's audio_content is binary.
        with open(os.path.join(self.path, filename), "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
