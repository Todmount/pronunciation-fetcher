import os
import sys

from dotenv import load_dotenv
from sources.free_dict_api import FetchFreeDictAPI
from sources.oxford_dict_scrape import ScrapeOxfordDict
from common.validation import normalize_words
from sources.audio_source_base import negative_responses

from rich.console import Console
from rich.prompt import Prompt, Confirm

load_dotenv()
console = Console()

providers = {
    1: ("Free Dictionary API", FetchFreeDictAPI),
    2: ("Oxford Dictionary", ScrapeOxfordDict),
    # 3: ("Merriam-Webster API", SomeOtherProvider),
}

def try_again() -> list:
    if (
        console.input("No valid words detected. Enter again? (Y/n): ").lower()
        not in negative_responses
    ):
        return normalize_words(input("Enter words (comma-separated): "))
    else:
        exit(0)

def get_user_input():
    user_input = input("Enter words (comma-separated): ")
    while not user_input:
        if not Confirm.ask("Input is empty. Enter again?", default="True"):
            print("Exiting...")
            raise SystemExit(0)
        user_input = input("Enter words (comma-separated): ")
    return user_input

# TO-DO: make user not able to use specific API
def check_api_key(provider: str):
    if provider != "merriam-webster":
        print("No API key required for this source.")
        return
    api_key = os.getenv("MW_API_KEY")
    if not api_key:
        console.print("No API key found. You would not be able to use this source.")



def choose_provider():
    # Show options
    console.print("\n[bold]Choose a provider:[/bold]")
    for num, (name, _) in providers.items():
        console.print(f"  {num}: [cyan]{name}[/cyan]")

    # Convert to string choices
    valid_choices = [str(k) for k in providers.keys()]

    user_choice_str = Prompt.ask(
        "\nEnter choice",
        choices=valid_choices,
        show_choices=False
    )

    user_choice = int(user_choice_str)  # Convert back to int
    name, provider_class = providers[user_choice]
    console.print(f"Selected: [green]{name}[/green]")
    return provider_class


def main(output_dir: str = "downloads", failed: list = ()):

    # user_input = (
    #     "none,one, two,   three,    four,none,one ,two  ,three   ,"
    #     "four    ,one one,two  two,three   three,four    four, '3, .hack_the_system.exe,"
    #     "69 "
    # )

    provider_class = choose_provider()
    if not failed:
        user_input = get_user_input()
        words, _ = normalize_words(user_input)
    else:
        words = failed

    fetcher = provider_class(output_dir=output_dir)
    fetcher.run(words=words)

    if fetcher.failed:
        reattempt_folder: str = "downloads/failed_reattempts"
        failed_words: list = fetcher.failed
        prompt = "\nWould you like to re-fetch failed words from another source? (Y/n): "
        if console.input(prompt).lower() not in negative_responses:
            main(output_dir=reattempt_folder, failed=failed_words)


if __name__ == "__main__":
    try:
        # check_api_key("merriam-webster")
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        exit(0)
    except NotADirectoryError:
        console.print(
            "\n[red]Error: Somehow, default output directory is not a directory.[/red]"
        )
        exit(1)