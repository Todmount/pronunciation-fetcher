import logging
from abc import ABC, abstractmethod
from rich.console import Console

from common.validation import (
    validate_word,
    validate_path,
    normalize_words,
    negative_responses,
)

logger = logging.getLogger(__name__)


class WordNotFound(Exception):
    pass


class AudioNotFound(Exception):
    pass


class DownloadError(Exception):
    pass


class GetAudio(ABC):

    def __init__(self, output_dir: str = "downloads", name: str = ""):
        self.output_dir = output_dir
        self.failed: list = []
        self.reasons: list = []
        self.done: list = []
        self.console = Console()
        self.name: str = name
        self.using()

    def using(self):
        self.console.print(f"\nYou are using {self.name}!\n", justify="center")

    def add_to_failed(self, word: str, reason: str) -> None:
        if word not in self.failed:
            self.failed.append(word)
        self.reasons.append(reason)

    def words_input(self) -> list:
        try:
            x = input("Provide words to search separated by comma: ")
            word_list = normalize_words(x)
            return word_list
        except KeyboardInterrupt:
            exit(0)

    @abstractmethod
    def download_audio(self, word: str) -> None:
        pass

    def process_words(self, words: list) -> None:
        for entry in words:
            status = validate_word(entry)
            if status != "valid":
                print(f"[!] Skipping '{entry}': {status}")
                continue
            if entry in self.done or entry in self.failed:
                continue

            try:
                print(f"Fetching pronunciation for: {entry}")
                self.download_audio(word=entry)
                self.done.append(entry)
            except WordNotFound as e:
                print(f"[!] {e}")
                self.add_to_failed(entry, reason="Word not found")
            except AudioNotFound as e:
                print(f"[!] {e}")
                self.add_to_failed(entry, reason="Audio not found")
            except DownloadError as e:
                print(f"[!] {e}")
                self.add_to_failed(entry, reason="Download error")
            except Exception as e:
                print(f'[!] Unexpected error for "{entry}"')
                self.add_to_failed(entry, reason=f"Unexpected error {e}")

    def show_results(self) -> None:
        """Display results summary"""
        if not self.failed:
            print(f"\nAll {len(self.done)} words fetched successfully!")
        elif (
            self.failed
            and input(
                f"Show {len(self.failed)} failed {'word' if len(self.failed)==1 else 'words'}? (Y/n): "
            ).lower()
            not in negative_responses
        ):
            try:
                print("Failed: ")
                for word, reason in zip(self.failed, self.reasons):
                    print(f" - '{word}': {reason}")
            except Exception as e:
                print(f"[!] Unexpected error while processing reasons ({e})")
                print(
                    f"{'-'*80}Failed to fetch pronunciation for: {', '.join(self.failed)}"
                )

    def run(self, words: list = None) -> None:
        validate_path(self.output_dir)
        if words is None:
            words = self.words_input()
        self.process_words(words)
        self.show_results()
