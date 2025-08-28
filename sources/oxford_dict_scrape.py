import os
import requests
import logging

from bs4 import BeautifulSoup

from sources.audio_source_base import (
    GetAudio,
    WordNotFound,
    AudioNotFound,
    DownloadError,
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

    def fetch_dict_page(self, word: str):
        word = word.lower()
        url = f"https://www.oxfordlearnersdictionaries.com/definition/english/{word}"

        logger.info(f"[🔍] Looking up: {word}")

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 404:
                raise WordNotFound(f"Word not found: {word}")
            elif response.status_code != 200:
                raise DownloadError(
                    f"Failed to fetch page. Status code: {response.status_code}"
                )
        except requests.exceptions.RequestException as de:
            raise DownloadError(f"Failed to fetch page: {de}")

        return BeautifulSoup(response.text, "html.parser")

    def extract_audio_url(self, word: str) -> str:
        soup = self.fetch_dict_page(word)
        button = soup.find("div", class_="sound audio_play_button pron-us icon-audio")
        if not button:
            raise AudioNotFound(f"Audio not found for: {word}")

        ogg_url = button.get("data-src-ogg")
        if not ogg_url:
            raise AudioNotFound(f"Audio not found for: {word}")

        # Ensure full URL
        if ogg_url.startswith("/"):
            ogg_url = "https://www.oxfordlearnersdictionaries.com" + ogg_url

        logger.info(f"[✔] OGG found: {ogg_url}")
        return ogg_url

    def download_audio(self, word: str, api: str) -> None:
        ogg_url = self.extract_audio_url(word)
        try:
            audio_response = requests.get(ogg_url, headers=self.headers, timeout=10)
            if audio_response.status_code != 200:
                raise DownloadError(
                    f"Failed to download audio. Status code: {audio_response.status_code}"
                )
            file_path = os.path.join(self.output_dir, f"{word}_us.ogg")
            with open(file_path, "wb") as f:
                f.write(audio_response.content)
            logger.info(f"[💾] Saved to: {file_path}")
        except requests.exceptions.RequestException as re:
            print(f"\t[!] Error downloading audio: {re}")
