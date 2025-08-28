import logging

from bs4 import BeautifulSoup

from sources.audio_source_base import (
    GetAudio,
    AudioNotFound,
)

logger = logging.getLogger(__name__)


class ScrapeOxfordDict(GetAudio):

    def __init__(self, output_dir: str = "downloads"):
        super().__init__(
            output_dir,
            name="Oxford Learner's Dictionary Scraper",
            process_name="Scraping",

        )
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
            ),
            "Referer": "https://www.oxfordlearnersdictionaries.com/",
            "Accept": "*/*",
            "Connection": "keep-alive",
        }

    def built_url(self, word: str, api_key: str):
        return f"https://www.oxfordlearnersdictionaries.com/definition/english/{word}"

    def parse_response(self, response):
        return BeautifulSoup(response.text, "html.parser")

    def extract_candidate(self, data):
        button = data.find("div", class_="sound audio_play_button pron-us icon-audio")
        if not button:
            raise AudioNotFound

        return button.get("data-src-mp3")

    def normalize_url(self, raw):
        audio_url = raw
        if not audio_url:
            raise AudioNotFound
        # Ensure full URL
        if audio_url.startswith("/"):
            audio_url = "https://www.oxfordlearnersdictionaries.com" + audio_url
        return audio_url
