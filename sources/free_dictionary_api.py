import logging

from sources.audio_pipeline import (
    AudioPipeline,
    AudioNotFound,
)

logger = logging.getLogger(__name__)


class FreeDictAPIFetcher(AudioPipeline):

    def __init__(self, output_dir: str = "downloads"):
        super().__init__(output_dir, name="FreeDict API")
        self.country_codes = ["us"]

    def get_word_url(self, word: str, api_key: str):
        return f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    def parse_word_response(self, response):
        return response.json()

    def extract_candidate(self, data):
        audio_urls = [
            phonetic.get("audio")
            for meaning in data
            for phonetic in meaning.get("phonetics", [])
            if phonetic.get("audio")
            and any(c in phonetic.get("audio").lower() for c in self.country_codes)
        ]
        if not audio_urls:
            raise AudioNotFound
        return audio_urls

    def normalize_audio_url(self, raw):
        audio_url = raw[0]
        return audio_url
