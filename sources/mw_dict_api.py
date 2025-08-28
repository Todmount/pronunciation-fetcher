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
    def fetch_word(self, word: str, api_key: str):
        if api_key is None:
            raise ValueError("No API key provided")
        url = f"https://www.dictionaryapi.com/api/v3/references/learners/json/{word}?key={api_key}"
        word_response = requests.get(url, timeout=10)
        if word_response.status_code == 404:
            raise WordNotFound(f"Word not found: {word}")
        elif word_response.status_code != 200:
            raise DownloadError(
                f"Failed to fetch page. Status code: {word_response.status_code}"
            )
        data = word_response.json()
        return data

    def collect_audio_urls(self, word: str, api_key: str) -> str:
        data = self.fetch_word(word, api_key)
        # if data[0] is not dict:
        #     raise NotImplementedError("Sometime there will be \"did you mean x?\""
        #                      "For now try to use another source.")
        print(f"data type: {type(data)}")
        print(f"data[0] type: {type(data[0])}")
        try:
            audio_filename = data[0].get("hwi", {}).get("prs", [])[0].get("sound", {}).get("audio")
            if audio_filename[0].isdigit() or not audio_filename[0].isalpha():
                subdir = "number"
            elif audio_filename.startswith("gg"):
                subdir = "gg"
            else:
                subdir = audio_filename[0]
        except AudioNotFound:
            raise
        except AttributeError as e:
            raise NotImplementedError(
                f"Case not implemented: API response 'did you mean x?' "
                f"Raw data: {data[:1]}"
            ) from e

        return f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{subdir}/{audio_filename}.mp3"

    def download_audio(self, word: str, api: str) -> None:
        audio_url = self.collect_audio_urls(word, api)
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