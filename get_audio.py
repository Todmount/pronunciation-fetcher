from sources.free_dict_api import FetchFreeDictAPI
from sources.oxford_dict_scrape import ScrapeOxfordDict
from common.validation import normalize_words
from sources.audio_source_base import negative_responses

from rich.console import Console
from rich.panel import Panel

# from rich.table import Table


if __name__ == "__main__":
    console = Console()
    console.print(
        Panel.fit(
            "Welcome to audio fetcher (name in work)!",
        ),
        justify="center",
    )

    user_input = (
        "none,one, two,   three,    four,none,one ,two  ,three   ,"
        "four    ,one one,two  two,three   three,four    four"
    )
    # user_input = input("Enter words separated by commas: ")
    words = normalize_words(user_input)

    fetcher = FetchFreeDictAPI(output_dir="downloads")
    fetcher.run(words=words)

    if fetcher.failed:
        reattempt_folder="downloads/failed_reattempts"
        prompt = "Would you like to try fetch failed from another source? (Y/n): "
        if input(prompt).lower() not in negative_responses:
            console.print(f"It will be saved to: '{reattempt_folder}'")
            scraper = ScrapeOxfordDict(output_dir=reattempt_folder)
            scraper.run(words=fetcher.failed)
