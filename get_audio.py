import os

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, Confirm

from sources.free_dict_api import FetchFreeDictAPI
from sources.mw_dict_api import FetchMWDictAPI
from sources.oxford_dict_scrape import ScrapeOxfordDict
from common.validation import normalize_words, negative_responses, exit_responses
from sources.audio_source_base import GetAudio

load_dotenv()
console = Console()

providers = {
    1: ("Merriam-Webster API", FetchMWDictAPI),  # mocking with free dict api
    2: ("Free Dictionary API", FetchFreeDictAPI),
    3: (f"Scrape Oxford Learner's Dictionary", ScrapeOxfordDict),
}

needs_api = ["Merriam-Webster API"]


def reprint_intro() -> bool:
    choices = ["y", "n", "exit"]
    _ = Prompt.ask(
        "What would you like to do?:",
        choices=choices,
        show_choices=True,
        default="Y"
    )
    if _ == "exit":
        raise SystemExit(0)
    elif _ == "n":
        return False
    return True


def user_api_input():
    api_key = Prompt.ask("Enter Merriam-Webster API key")
    with open(".env", "w") as f:
        f.write(f"MW_API_KEY={api_key}")


def get_words_input():
    user_input = input("Enter words (comma-separated): ")
    while not user_input:
        if not Confirm.ask("Input is empty. Enter again?", default="True"):
            print("Exiting...")
            raise SystemExit(0)
        user_input = input("Enter words (comma-separated): ")
    return user_input


# TODO: make a user not able to use a specific provider if no API
# TODO: implement proper API validation
def check_api_key(provider: str) -> bool:
    if provider not in needs_api:
        # logger.info("No API key required for this source.")
        return True
    api_key = os.getenv("MW_API_KEY")
    if not api_key:
        return False
    return True


def choose_provider() -> tuple[str, type[GetAudio]]:
    console.print("\n[bold]Choose a provider:[/bold]")
    for num, (name, _) in providers.items():
        console.print(f"  {num}: [cyan]{name}[/cyan]")
    console.print("  Enter 'exit' or 'q' to exit")
    console.print("\n[dim]Notes:[/dim]")
    console.print("[dim]• Merriam-Webster requires a personal API key[/dim]")
    console.print("[dim]• Oxford scraping: use sparingly to avoid IP bans[/dim]")

    valid_choices = [str(k) for k in (providers.keys())]
    valid_choices.extend(exit_responses)

    user_choice_str = Prompt.ask(
        "\nEnter choice", choices=valid_choices, show_choices=False
    )

    if user_choice_str in exit_responses:
        print("Exiting...")
        raise SystemExit(0)

    user_choice = int(user_choice_str)  # Convert back to int
    name, provider_class = providers[user_choice]
    console.print(f"Selected: [green]{name}[/green]")
    return name, provider_class


def main(output_dir: str = "downloads", failed: list = ()):

    # user_input = (
    #     "none,one, two,   three,    four,none,one ,two  ,three   ,"
    #     "four    ,one one,two  two,three   three,four    four, '3, .hack_the_system.exe,"
    #     "69 "
    # )

    provider, provider_class = choose_provider()
    if not check_api_key(provider):
        user_api: str | None = None
        console.print("No API key found. You would not be able to use this source.")
        main() if reprint_intro() else user_api_input()
    else:
        user_api = os.getenv("MW_API_KEY")
    if not failed:
        user_input: str = get_words_input()
        words, _ = normalize_words(user_input)
    else:
        words = failed

    if len(words) > 100:
        console.print(
            "Too many words (>100). Batched processing not yet supported"
            "\nConsider smaller sets of words and try again."
            "\nExiting..."
        )
        raise SystemExit(1)

    fetcher = provider_class(output_dir=output_dir)
    fetcher.run(words=words, api=user_api)

    if fetcher.failed:
        reattempt_folder: str = "downloads/failed_reattempts"
        failed_words: list = fetcher.failed
        prompt = (
            "\nWould you like to re-fetch failed words from another source? (Y/n): "
        )
        if console.input(prompt).lower() not in negative_responses:
            main(output_dir=reattempt_folder, failed=failed_words)


if __name__ == "__main__":
    continue_running = True
    while continue_running:
        try:
            main()
            x = input("Press enter to continue or 'q' to exit: ")
            continue_running = x.lower() not in exit_responses
        except KeyboardInterrupt:
            print("\nExiting...")
            exit(0)
        except NotADirectoryError:
            console.print(
                "\n[red]Error: Somehow, default output directory is not a directory.[/red]"
            )
            exit(1)