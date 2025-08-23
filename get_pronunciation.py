import requests
import logging

from common.validation import *

logger = logging.getLogger(__name__)


class WordNotFound(Exception):
    pass


class AudioNotFound(Exception):
    pass


class DownloadError(Exception):
    pass


failed: list = []
reasons: list = []
done: list = []


def add_to_failed(word: str, reason: str) -> None:
    failed.append(word) if word not in failed else failed
    reasons.append(reason)


def words_input() -> list:
    try:
        x = input(f"Provide words to search separated by comma: ")
        word_list = normalize_words(x)
        return word_list
    except KeyboardInterrupt:
        exit(0)


def fetch_word(word: str):
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


def collect_audio_urls(word: str) -> list[str] | None:
    country = ["uk", "us"]
    data = fetch_word(word)
    try:
        audio_urls = [
            phonetic.get("audio")
            for meaning in data
            for phonetic in meaning.get("phonetics", [])
            if phonetic.get("audio")
            and any(c in phonetic.get("audio").lower() for c in country)
        ]
        if not audio_urls:
            raise AudioNotFound(f"Audio not found for: {word}")
        if len(audio_urls) > 1:
            audio_urls = [audio_urls[0]]
        logger.info(f"Audio found for: {word}")
        return audio_urls[0]
    except AudioNotFound as e:
        print(f"[!] {e}")
        return None


def download_audio(word: str, output_dir: str) -> None:
    audio_url = collect_audio_urls(word)
    if not audio_url:
        raise DownloadError(f"Audio not found for: {word}")
    try:
        audio_response = requests.get(audio_url, timeout=10)
        if audio_response.status_code == 200:
            file_path = os.path.join(output_dir, f"{word}.mp3")
            with open(file_path, "wb") as f:
                f.write(audio_response.content)
            logger.info(f"Saved to: {file_path}")
        else:
            raise DownloadError(
                f"Failed to download audio: {audio_response.status_code}"
            )
    except requests.exceptions.RequestException as re:
        print(f"\t[!] Error downloading audio: {re}")


if __name__ == "__main__":

    validate_path("downloads")
    # words = words_input()
    raw_input = (
        "none,one, two,   three,    four,none,one ,two  ,three   ,"
        "four    ,one one,two  two,three   three,four    four"
    )
    words = normalize_words(raw_input)
    for entry in words:
        try:
            status = validate_word(entry)
            if status != "valid":
                print(f"[!] Skipping '{entry}': {status}")
                continue
            else:
                logger.info(f"Fetching pronunciation for: {entry}")
                download_audio(word=entry, output_dir="downloads")
        except WordNotFound as e:
            print(f"[!] {e}")
