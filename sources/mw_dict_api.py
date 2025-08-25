import os
import requests
import logging

from sources.audio_source_base import (
    GetAudio,
    WordNotFound,
    AudioNotFound,
    DownloadError,
)

logger = logging.getLogger(__name__)


class FetchMWDictAPI(GetAudio):

    def __init__(self, output_dir: str = "downloads"):
        super().__init__(output_dir, name="Merriam-Webster API")
        self.country_codes = ["uk", "us"]

    # Mocking the API call
    def fetch_word(self, word: str):
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        word_response = requests.get(url, timeout=10)
        if word_response.status_code == 404:
            raise WordNotFound(f"Word not found: {word}")
        elif word_response.status_code != 200:
            raise DownloadError(
                f"Failed to fetch page. Status code: {word_response.status_code}"
            )
        data = word_response.json()
        return data

    def collect_audio_urls(self, word: str) -> str:
        data = self.fetch_word(word)
        try:
            audio_urls = [
                phonetic.get("audio")
                for meaning in data
                for phonetic in meaning.get("phonetics", [])
                if phonetic.get("audio")
                and any(c in phonetic.get("audio").lower() for c in self.country_codes)
            ]
            if not audio_urls:
                raise AudioNotFound(f"Audio not found for: {word}")
            if len(audio_urls) > 1:
                audio_urls = [audio_urls[0]]
            logger.info(f"Audio found for: {word}")
            return audio_urls[0]
        except AudioNotFound:
            raise

    def download_audio(self, word: str) -> None:
        audio_url = self.collect_audio_urls(word)
        if not audio_url:
            raise DownloadError(f"Audio not found for: {word}")
        try:
            audio_response = requests.get(audio_url, timeout=10)
            if audio_response.status_code == 200:
                file_path = os.path.join(self.output_dir, f"{word}.mp3")
                with open(file_path, "wb") as f:
                    f.write(audio_response.content)
                logger.info(f"Saved to: {file_path}")
            else:
                raise DownloadError(
                    f"Failed to download audio: {audio_response.status_code}"
                )
        except requests.exceptions.RequestException as re:
            print(f"\t[!] Error downloading audio: {re}")