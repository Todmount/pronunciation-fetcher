import logging
import os
import requests

from abc import ABC, abstractmethod
from rich.console import Console
from rich.progress import Progress
from rich.prompt import Confirm
from rich.table import Table
from typing import Any

from common.constants import PROJECT_ROOT

log = logging.getLogger("pf.audio")


class WordNotFound(Exception):
    pass


class AudioNotFound(Exception):
    pass


class DownloadError(Exception):
    pass


class AudioPipeline(ABC):

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

    def add_to_failed(self, word: str, reason: str) -> None:
        if word not in self.failed:
            self.failed.append(word)
        self.reasons.append(reason)

    @abstractmethod
    def get_word_url(self, word: str, api_key: str | None) -> str:
        """Built source-specific url for a word"""
        pass

    def fetch_word_data(self, word: str, api_key: str | None) -> Any:
        """
        Fetch and parse word data from the source.

        Steps:
            1. Build the word URL using `get_word_url()`.
            2. Perform the HTTP request.
            3. Raise exceptions for error status codes.
            4. Parse the response into structured data.

        Args:
            word: The word being processed.
            api_key: Source-specific API key, if required.

        Returns:
            Parsed, source-specific word data (format depends on implementation
            of `parse_word_response()`).

        Raises:
            WordNotFound: If the source reports the word is missing (404).
            DownloadError: For all other HTTP errors.
        """
        url = self.get_word_url(word, api_key)
        word = word.lower()
        word_response = requests.get(url, timeout=10, headers=self.headers)
        if word_response.status_code == 404:
            raise WordNotFound(f"Word not found: {word}")
        elif word_response.status_code != 200:
            raise DownloadError(
                f"Failed to fetch page. Status code: {word_response.status_code}"
            )
        return self.parse_word_response(word_response)

    @abstractmethod
    def parse_word_response(self, response: requests.Response) -> Any:
        """
        Parse the HTTP response for a word into a source-specific structured format.

        Args:
            response: The HTTP response object returned by `fetch_word()`.

        Returns:
            Source-specific parsed data (e.g., JSON, dict, or HTML object)
            that can be further processed by `extract_candidate()`.
        """
        pass

    def process_words(self, words: list, api: str = None) -> None:
        progress = Progress(
            "[progress.description]{task.description}",
            "[progress.percentage]{task.percentage:>3.0f}%",
            console=self.console,
        )
        progress.start()
        task = progress.add_task(
            f"Processing words...", total=len(words), style="bold cyan"
        )

        for entry in words:
            progress.update(task, advance=1, refresh=True)
            if entry in self.done or entry in self.failed:
                continue

            try:
                # print(f"Fetching pronunciation for: {entry}")
                self.download_audio(word=entry, api_key=api)
                self.done.append(entry)
            except WordNotFound:
                log.debug(f"Word not found: {entry}")
                self.add_to_failed(entry, reason="Word not found")
            except AudioNotFound:
                log.debug(f"Audio not found: {entry}")
                self.add_to_failed(entry, reason="Audio not found")
            except DownloadError as e:
                log.debug(f"Download failed for {entry}: {e}")
                self.add_to_failed(entry, reason="Download error")
            except NotImplementedError:
                log.debug(f"API response triggered unimplemented feature")
                self.add_to_failed(
                    entry,
                    reason="[MW exclusive] Triggered unimplemented 'did you mean x?'. "
                    "Try another source",
                )
            except Exception as e:
                log.debug(f"[!] Unexpected error for {entry} : {e}")
                self.add_to_failed(
                    entry, reason=f"Unexpected error. Try another source"
                )
            progress.stop()

    def display_failed_words_table(self):
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
            table.add_column("Reason", justify="center", style="green", no_wrap=True)

            for word, reason in zip(self.failed, self.reasons):
                table.add_row(word, reason)
            self.console.print(table)
            # self.console.print("")
        except Exception as e:
            log.error(f"Unexpected error while processing failed: {e}")
            self.console.print(
                f"{'-'*80}\nFailed to fetch pronunciation for: {', '.join(self.failed)}"
            )

    def show_results(self) -> None:
        log.info(
            f"Download completed: {len(self.done)} successful, {len(self.failed)} failed"
        )
        if not self.failed:
            log.info(f"All words fetched successfully!")
        elif self.failed and Confirm.ask(
            f"Show {len(self.failed)} failed {'word' if len(self.failed)==1 else 'words'}?",
            default=True,
        ):
            log.debug(f"User decided to print failed words table")
            self.display_failed_words_table()

    @abstractmethod
    def extract_candidate(self, data) -> str:
        """
        Extract the raw audio URL from fetched word data.

        Args:
            data: The raw data returned by fetch_word().

        Returns:
            str: The "raw" extracted audio URL (may need normalization).
        """
        pass

    @abstractmethod
    def normalize_audio_url(self, raw: str) -> str:
        """
        Normalize the audio URL according to source-specific rules.

        Args:
            raw: The raw URL extracted by extract_candidate().

        Returns:
            Normalized URL ready for passing to wrapper.
        """
        pass

    def get_audio_url(self, word: str, api_key: str | None) -> str:
        """
        Processes a word through the full audio URL pipeline: fetch, extract, normalize.

        Args:
            word: Word being processed.
            api_key: Source-specific API key, if required.

        Returns:
            Audio URL ready for downloading.
        """
        log.debug(f"Fetching audio URL for: {word}")
        data = self.fetch_word_data(word, api_key)

        candidates = self.extract_candidate(data)
        if not candidates:
            raise AudioNotFound

        url = self.normalize_audio_url(candidates)
        log.debug(f"Audio found: {url}")
        return url

    def download_audio(self, word: str, api_key: str | None) -> None:
        """Download audio for a word and save to self.output_dir. Raises DownloadError on failure."""
        audio_url = self.get_audio_url(word, api_key)
        if not audio_url:
            raise DownloadError(f"Audio not found for: {word}")
        try:
            audio_response = requests.get(audio_url, headers=self.headers, timeout=10)
            if audio_response.status_code == 200:
                file_path = os.path.join(self.output_dir, f"{word}.mp3")
                with open(file_path, "wb") as f:
                    f.write(audio_response.content)
                log.debug(f"Saved to: {PROJECT_ROOT/file_path}")
            else:
                raise DownloadError(
                    f"Failed to download audio. Status code: {audio_response.status_code}"
                )

        except requests.exceptions.RequestException as re:
            log.error(f"Error downloading audio: {re}")

    def run(self, words: list, api: str | None) -> None:
        log.info(f"Starting download with {self.name} for {len(words)} words")
        self.process_words(words, api)
        self.show_results()
