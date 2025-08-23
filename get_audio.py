from sources.free_dict_api import FetchFreeDictAPI
from sources.oxford_dict_scrape import ScrapeOxfordDict
from common.validation import normalize_words
from sources.audio_source_base import negative_responses

from rich.console import Console
from rich.panel import Panel


if __name__ == "__main__":
    console = Console()
    console.print(
        Panel.fit(
            "Welcome to audio fetcher (name in work)!",
        ),
        justify="center",
    )

    # user_input = (
    #     "none,one, two,   three,    four,none,one ,two  ,three   ,"
    #     "four    ,one one,two  two,three   three,four    four, '3, .hack_the_system.exe,"
    #     "69 "
    # )

    user_input = input("Enter words separated by commas: ")
    words, _ = normalize_words(user_input) if user_input else []

    def try_again() -> list:
        if input("Try again? (Y/n): ").lower() not in negative_responses:
            return normalize_words(input("Enter words separated by commas: "))
        else:
            exit(0)

    while not words:
        words = try_again()

    fetcher = FetchFreeDictAPI(output_dir="downloads")
    fetcher.run(words=words)

    if fetcher.failed:
        reattempt_folder = "downloads/failed_reattempts"
        prompt = "Would you like to try fetch failed from another source? (Y/n): "
        if input(prompt).lower() not in negative_responses:
            console.print(f"It will be saved to: '{reattempt_folder}'")
            scraper = ScrapeOxfordDict(output_dir=reattempt_folder)
            scraper.run(words=fetcher.failed)
