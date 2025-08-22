import os
import requests
import shutil
import logging
import string
from bs4 import BeautifulSoup

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

negative_responses: set = {"no", "n", "nope", "-"}


def add_to_failed(word: str, reason: str) -> None:
    failed.append(word) if word not in failed else failed
    reasons.append(reason)


def validate_path(path) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
        print(f'Created directory: "{path}"')
    if os.path.exists(path) and os.path.isdir(path):
        x = input(
            f'[!] Path "{path}" already exists. Script will clear it. Continue? (Y/n): '
        ).lower()
        if x != negative_responses:
            shutil.rmtree(path)
            os.makedirs(path)
        else:
            print("Aborted by user.")
            exit(0)


def validate_word(word: str) -> str:
    allowed_chars = string.ascii_letters + "-`'"
    if not word:
        return "empty"
    if word.isnumeric():
        return "numeric"
    if not all(char in allowed_chars for char in word):
        return "invalid characters"
    return "valid"


def words_input() -> list:
    try:
        x = input(f"Provide words to search separated by space: ")
        word_list = x.split()
        return word_list
    except KeyboardInterrupt:
        exit(0)


def fetch_us_ogg(word: str, output_dir: str = "downloads") -> None:
    # Construct Oxford URL for the word
    word.lower()
    url = f"https://www.oxfordlearnersdictionaries.com/definition/english/{word}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
        ),
        "Referer": "https://www.oxfordlearnersdictionaries.com/",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }

    # Step 1: Fetch the HTML page
    logger.info(f"[🔍] Looking up: {word}")

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            raise WordNotFound(f"Word not found: {word}")
        elif response.status_code != 200:
            raise DownloadError(
                f"Failed to fetch page. Status code: {response.status_code}"
            )
    except requests.exceptions.RequestException as de:
        raise DownloadError(f"Failed to fetch page: {de}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Step 2: Find the US pronunciation .ogg URL
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

    # Step 3: Download the audio file
    try:
        audio_response = requests.get(ogg_url, headers=headers, timeout=10)
        if audio_response.status_code != 200:
            raise DownloadError(
                f"Failed to download audio. Status code: {audio_response.status_code}"
            )
        file_path = os.path.join(output_dir, f"{word}_us.ogg")
        with open(file_path, "wb") as f:
            f.write(audio_response.content)
        logger.info(f"[💾] Saved to: {file_path}")
    except requests.exceptions.RequestException as re:
        print(f"\t[!] Error downloading audio: {re}")


if __name__ == "__main__":

    print(
        "Welcome to Oxford Dictionary Audio Scrapper!"
        "\nThis script will download the US pronunciation .ogg audio file for each word you provide."
        "\nScript will save files to the downloads folder inside project root."
        "\nAs for now it only supports single words."
    )

    validate_path("downloads")
    words = words_input()

    for entry in words:
        status = validate_word(entry)
        if status != "valid":
            print(f"[!] Skipping '{entry}': {status}")
            continue
        if entry in done or entry in failed:
            continue
        try:
            print(f"Fetching pronunciation for: {entry}")
            fetch_us_ogg(word=entry, output_dir="downloads")
            done.append(entry)
        except WordNotFound as e:
            print(f"[!] {e}")
            add_to_failed(entry, reason="Word not found")
        except AudioNotFound as e:
            print(f"[!] {e}")
            add_to_failed(entry, reason="Audio not found")
        except DownloadError as e:
            print(f"[!] {e}")
            add_to_failed(entry, reason="Download error")
        except Exception as e:
            print(f'[!] Unexpected error for "{entry}": {e}')
            add_to_failed(entry, reason=f"Unexpected error {e}")

    if not failed:
        print(f"\nAll {len(done)} words fetched successfully!")
    elif (
        failed
        and input(f"Show {len(failed)} failed words? (Y/n): ").lower()
        not in negative_responses
    ):
        try:
            print("Failed: ")
            for word, reason in zip(failed, reasons):
                print(f" - '{word}': {reason}")
        except Exception as e:
            print(f"[!] Unexpected error while processing reasons {e}")
            print(f"Failed to fetch pronunciation for: {', '.join(failed)}")
