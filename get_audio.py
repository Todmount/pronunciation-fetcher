from sources.free_dict_api import FetchFreeDictAPI
from sources.oxford_dict_scrape import ScrapeOxfordDict
from common.validation import normalize_words
from sources.audio_source_base import negative_responses

from rich.console import Console

console = Console()


def try_again() -> list:
    if (
            console.input("No valid words detected. Enter again? (Y/n): ").lower()
            not in negative_responses
    ):
        return normalize_words(input("Enter words (comma-separated): "))
    else:
        exit(0)

def main():

    # user_input = (
    #     "none,one, two,   three,    four,none,one ,two  ,three   ,"
    #     "four    ,one one,two  two,three   three,four    four, '3, .hack_the_system.exe,"
    #     "69 "
    # )

    user_input = console.input("Enter words (comma-separated): ")
    words, _ = normalize_words(user_input) if user_input else [(), ()]

    while not words:
        words = try_again()

    fetcher = FetchFreeDictAPI(output_dir="downloads")
    fetcher.run(words=words)

    if fetcher.failed:
        reattempt_folder = "downloads/failed_reattempts"
        prompt = "\nWould you like to re-fetch failed words from another source? (Y/n): "
        if console.input(prompt).lower() not in negative_responses:
            # console.print(f"It will be saved to: '{reattempt_folder}'")
            scraper = ScrapeOxfordDict(output_dir=reattempt_folder)
            scraper.run(words=fetcher.failed)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        exit(0)
    except NotADirectoryError:
        console.print(
            "\n[red]Error: Somehow, default output directory is not a directory.[/red]"
        )
        exit(1)