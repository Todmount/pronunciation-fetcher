import logging

from sources.audio_source_base import (
    GetAudio,
    AudioNotFound,
)

logger = logging.getLogger(__name__)


class FetchMWDictAPI(GetAudio):

    def __init__(self, output_dir: str = "downloads"):
        super().__init__(output_dir, name="Merriam-Webster API")
        self.country_codes = ["uk", "us"]

    def built_url(self, word: str, api_key: str):
        if api_key is None:
            raise ValueError("No API key provided")
        return f"https://www.dictionaryapi.com/api/v3/references/learners/json/{word}?key={api_key}"

    def parse_response(self, response):
        return response.json()

    def extract_candidate(self, data):
        try:
            audio_filename = data[0].get("hwi", {}).get("prs", [])[0].get("sound", {}).get("audio")
            if not audio_filename:
                raise AudioNotFound
            if audio_filename[0].isdigit() or not audio_filename[0].isalpha():
                subdir = "number"
            elif audio_filename.startswith("gg"):
                subdir = "gg"
            else:
                subdir = audio_filename[0]
            return audio_filename, subdir
        except AttributeError as e:
            raise NotImplementedError(
                f"Case not implemented: API response 'did you mean x?' "
                f"Raw data: {data[:1]}"
            ) from e

    def normalize_url(self, raw):
        audio_filename, subdir = raw
        return f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{subdir}/{audio_filename}.mp3"