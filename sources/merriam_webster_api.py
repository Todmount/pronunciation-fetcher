import logging

from sources.audio_pipeline import (
    AudioPipeline,
    AudioNotFound,
)

logger = logging.getLogger(__name__)


class MerriamWebsterDictAPIFetcher(AudioPipeline):

    def __init__(self, output_dir: str = "downloads"):
        super().__init__(output_dir, name="Merriam-Webster API")
        self.country_codes = ["uk", "us"]

    def get_word_url(self, word: str, api_key: str) -> str:
        if api_key is None:
            raise ValueError("No API key provided")
        return f"https://www.dictionaryapi.com/api/v3/references/learners/json/{word}?key={api_key}"

    def parse_word_response(self, response):
        return response.json()

    def find_audio(self, data) -> str:
        """Additional search logic for Merriam-Webster. For now, it just takes all audio in a list and returns the first element"""
        audio_files = []

        for entry in data:
            # 1) Normal case: pronunciation in hwi.prs
            if "hwi" in entry:
                for prs in entry["hwi"].get("prs", []):
                    if "sound" in prs:
                        audio_files.append(prs["sound"]["audio"])
            # 2) Variant case: pronunciation in vrs[i].prs
            for vr in entry.get("vrs", []):
                for prs in vr.get("prs", []):
                    if "sound" in prs:
                        audio_files.append(prs["sound"]["audio"])

        return audio_files[0]

    def extract_candidate(self, data):
        try:
            audio_filename = self.find_audio(data)
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

    def normalize_audio_url(self, raw):
        audio_filename, subdir = raw
        return f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{subdir}/{audio_filename}.mp3"
