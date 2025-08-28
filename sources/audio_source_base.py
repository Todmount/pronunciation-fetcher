import os
import logging
import requests

from abc import ABC, abstractmethod

from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from common.validation import validate_path, negative_responses

logger = logging.getLogger(__name__)
# Configure logger
logging.basicConfig(
    filename="logs/my_log.log",       # path to external file
    filemode="a",                # "a" = append, "w" = overwrite each run
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO           # minimum level to log
)

class WordNotFound(Exception):
    pass


class AudioNotFound(Exception):
    pass


class DownloadError(Exception):
    pass


class GetAudio(ABC):

    def __init__(
        self,
        output_dir: str = "downloads",
        name: str = "",
        process_name: str = "Fetching",
    ):
        self.headers = None
        self.output_dir = output_dir
        self.failed: list = []
        self.reasons: list = []
        self.done: list = []
        self.console = Console()
        self.name: str = name
        self.process_name: str = process_name
        self.using()

    def using(self):
        self.console.print(f"{self.process_name} {self.name}...", style="green")

    def add_to_failed(self, word: str, reason: str) -> None:
        if word not in self.failed:
            self.failed.append(word)
        self.reasons.append(reason)

    @abstractmethod
    def built_url(self, word: str, api_key: str):
        pass

    def fetch_word(self, word: str, api_key: str | None):
        url = self.built_url(word, api_key)
        word=word.lower()
        word_response = requests.get(url, timeout=10, headers=self.headers)
        if word_response.status_code == 404:
            raise WordNotFound(f"Word not found: {word}")
        elif word_response.status_code != 200:
            raise DownloadError(
                f"Failed to fetch page. Status code: {word_response.status_code}"
            )
        return self.parse_response(word_response)

    @abstractmethod
    def parse_response(self, response):
        pass

    def process_words(self, words: list, api: str = None) -> None:
        progress = Progress(
            "[progress.description]{task.description}",
            "[progress.percentage]{task.percentage:>3.0f}%",
            console=self.console,
        )
        progress.start()
        task = progress.add_task(
            f"Processing words...",
            total=len(words),
            style="bold cyan")

        for entry in words:
            progress.update(task, advance=1)
            if entry in self.done or entry in self.failed:
                continue

            try:
                # print(f"Fetching pronunciation for: {entry}")
                self.download_audio(word=entry, api=api)
                self.done.append(entry)
            except WordNotFound as e:
                logger.info(f"[!] {e}")
                self.add_to_failed(entry, reason="Word not found")
            except AudioNotFound as e:
                logger.info(f"[!] {e}")
                self.add_to_failed(entry, reason="Audio not found")
            except DownloadError as e:
                logger.info(f"[!] {e}")
                self.add_to_failed(entry, reason="Download error")
            except NotImplementedError as e:
                logger.info(f"[!] {e}")
                self.add_to_failed(
                    entry,
                    reason="[MW exclusive] Triggered unimplemented 'did you mean x?'. "
                           "Try another source")
            except Exception as e:
                logger.debug(f'[!] Unexpected error for "{entry} : {e}"')
                self.add_to_failed(entry, reason=f"Unexpected error: {e}. \nTry another source")
                raise e
        progress.stop()

    def show_results(self) -> None:
        if not self.failed:
            self.console.print(f"All words fetched successfully!")
        elif (
            self.failed
            and input(
                f"Show {len(self.failed)} failed {'word' if len(self.failed)==1 else 'words'}? (Y/n): "
            ).lower()
            not in negative_responses
        ):
            try:
                # print("Failed: ")
                table = Table(
                    show_lines=True,
                    show_header=True,
                    header_style="bold magenta",
                    expand=True,
                )
                table.add_column(
                    "Word",
                    justify="center",
                    style="cyan",
                    no_wrap=True,
                )
                table.add_column(
                    "Reason", justify="center", style="green", no_wrap=True
                )

                for word, reason in zip(self.failed, self.reasons):
                    table.add_row(word, reason)
                self.console.print(table)
                self.console.print("")
            except Exception as e:
                print(f"[!] Unexpected error while processing reasons ({e})")
                print(
                    f"{'-'*80}\nFailed to fetch pronunciation for: {', '.join(self.failed)}"
                )

    @abstractmethod
    def extract_candidate(self, data):
        pass

    @abstractmethod
    def normalize_url(self, raw):
        """
        Guess.
        Attention on type(raw) and its len
        """
        pass

    def collect_audio_url(self, word: str, api_key: str) -> str:
        data = self.fetch_word(word, api_key)

        candidates = self.extract_candidate(data)
        if not candidates:
            raise AudioNotFound

        url = self.normalize_url(candidates)
        logger.info(f"Audio found: {url}")
        return url

    def download_audio(self, word: str, api: str) -> None:
        audio_url = self.collect_audio_url(word, api)
        if not audio_url:
            raise DownloadError(f"Audio not found for: {word}")
        try:
            audio_response = requests.get(audio_url, headers=self.headers, timeout=10)
            if audio_response.status_code == 200:
                file_path = os.path.join(self.output_dir, f"{word}.mp3")
                with open(file_path, "wb") as f:
                    f.write(audio_response.content)
                logger.info(f"[💾] Saved to: {file_path}")
            else:
                raise DownloadError(
                    f"Failed to download audio. Status code: {audio_response.status_code}"
                )

        except requests.exceptions.RequestException as re:
            print(f"\t[!] Error downloading audio: {re}")

    def run(self, words: list = None, api: str = None) -> None:
        validate_path(self.output_dir)
        self.process_words(words, api)
        self.show_results()
