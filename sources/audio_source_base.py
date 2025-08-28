import logging

from abc import ABC, abstractmethod
from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from common.validation import validate_path, negative_responses

logger = logging.getLogger(__name__)


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
    def download_audio(self, word: str, api: str) -> None:
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
                logger.info(f'[!] Unexpected error for "{entry}"')
                self.add_to_failed(entry, reason=f"Unexpected error: {e}. \nTry another source")
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

    def run(self, words: list = None, api: str = None) -> None:
        validate_path(self.output_dir)
        self.process_words(words, api)
        self.show_results()
