import os

from dotenv import load_dotenv
from sources.free_dict_api import FetchFreeDictAPI
from sources.oxford_dict_scrape import ScrapeOxfordDict
from common.validation import normalize_words
from sources.audio_source_base import negative_responses

from rich.console import Console

load_dotenv()
console = Console()
user_api_access = {
    "merriam-webster": False,
}
provider_list = ["merriam-webster"]

# MW_API_KEY = os.getenv("MW_API_KEY")


def try_again() -> list:
    if (
            console.input("No valid words detected. Enter again? (Y/n): ").lower()
            not in negative_responses
    ):
        return normalize_words(input("Enter words (comma-separated): "))
    else:
        exit(0)

def check_api_key(provider: str):
    choice = None

    if provider not in provider_list:
        console.print("Invalid provider. Check input and try again.")
        raise SystemExit
    mw_api_key = os.getenv(provider)
    if not mw_api_key:
        console.print(
            "\n[red]Error: Merriam-Webster API key not found.[/red]"
        )
        choice = console.input("Would you like to provide one?"
                          "\n[!] Choosing 'n' will block your access to fetch from Merriam-Webster API (Y/n): ")
    if choice.lower() in negative_responses:
        console.print("You will not be able to fetch from Merriam-Webster API.")
        user_api_access["merriam-webster"] = False
    else:
        user_api_input = console.input("Enter your Merriam-Webster API key: ")
        if user_api_input:
            os.environ["MW_API_KEY"] = user_api_input
            user_api_access["merriam-webster"] = True



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
        check_api_key(provider="merriam-webster")
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        exit(0)
    except NotADirectoryError:
        console.print(
            "\n[red]Error: Somehow, default output directory is not a directory.[/red]"
        )
        exit(1)