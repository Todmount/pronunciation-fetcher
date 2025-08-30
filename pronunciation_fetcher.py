import os
import logging

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, Confirm

from sources.free_dictionary_api import FreeDictAPIFetcher
from sources.merriam_webster_api import MerriamWebsterDictAPIFetcher
from sources.oxford_dictionary_scraper import OxfordDictScraper
from common.validation import normalize_words, exit_responses, validate_path
from sources.audio_pipeline import AudioPipeline

load_dotenv()
console = Console()
logger = logging.getLogger(__name__)

providers = {
    1: (
        "Merriam-Webster API",
        {"class": MerriamWebsterDictAPIFetcher, "env": "MW_API_KEY"},
    ),
    2: ("Free Dictionary API", {"class": FreeDictAPIFetcher}),
    3: (f"Scrape Oxford Learner's Dictionary", {"class": OxfordDictScraper}),
}

needs_api = ["Merriam-Webster API"]


def reprint_intro() -> bool:
    choices = ["c", "a", "exit", "q"]
    console.print("\n[bold]What would you like to do?[/bold]")
    console.print("  c: [cyan]Choose another source[/cyan]")
    console.print("  a: [cyan]Enter API key[/cyan]")
    console.print("  Enter 'exit' or 'q' to exit")
    prompt = Prompt.ask(
        "Enter choice", choices=choices, show_choices=False, default="c"
    )
    if prompt in ["exit", "q"]:
        raise SystemExit(0)
    elif prompt == "a":
        return False
    else:
        return True


def user_api_input(provider: str, env_var: str):
    api_key = Prompt.ask(f"Enter {provider} key")
    with open(".env", "w") as f:
        f.write(f"{env_var}={api_key}")
    return api_key


# TODO: implement proper API validation
def check_api_key(provider: str, env_var: str) -> bool:
    if provider not in needs_api:
        logger.info("No API key required for this source.")
        return True
    api_key = os.getenv(env_var)
    if not api_key:
        return False
    return True


def choose_provider() -> tuple[str, type[AudioPipeline], str]:
    console.print("\n[b]Choose a provider:[/b]")
    for num, (name, _) in providers.items():
        console.print(f"  {num}: [cyan]{name}[/cyan]")
    console.print("  Enter 'exit' or 'q' to exit")
    # console.print("\n[dim]Notes:[/dim]")
    # console.print("[dim]• Merriam-Webster requires a personal API key[/dim]")
    # console.print("[dim]• Oxford scraping: use sparingly to avoid IP bans[/dim]")

    valid_choices = [str(k) for k in (providers.keys())]
    valid_choices.extend(exit_responses)

    user_choice_str = Prompt.ask(
        "\nEnter choice", choices=valid_choices, show_choices=False
    )

    if user_choice_str in exit_responses:
        print("Exiting...")
        raise SystemExit(0)

    user_choice = int(user_choice_str)
    provider_info = providers[user_choice]
    name, details = provider_info
    env = details.get("env")
    provider_class = details["class"]

    console.print(f"Selected: [green]{name}[/green]")
    return name, provider_class, env


def choose_input_format() -> str:
    console.print("\n[b]How would you like to provide words?[/b]")
    console.print("  1. Type them directly in the terminal")
    console.print("  2. Load them from a .txt file")
    console.print("  Enter 'exit' or 'q' to quit")
    # console.print("\n[dim]Notes:[/dim]")
    # console.print("[dim]• You can enter up to 100 words at a time[/dim]")
    # console.print("[dim]• Words should be separated by commas[/dim]")
    # console.print("[dim]• Non-letter characters will be ignored[/dim]")
    # console.print(
    #     "[dim]• By default, the app looks for 'words.txt' in the project root[/dim]"
    # )

    valid_choices = ["1", "2"]
    valid_choices.extend(exit_responses)

    user_choice = Prompt.ask("\nEnter", choices=valid_choices, show_choices=False)

    if user_choice == "1":
        return "manual"
    elif user_choice == "2":
        return "load_txt"
    else:
        print("Exiting...")
        raise SystemExit(0)


def manual_words_input():
    user_input = console.input("Enter words (comma-separated): ")
    while not user_input:
        if not Confirm.ask("Input is empty. Enter again?", default="True"):
            print("Exiting...")
            raise SystemExit(0)
        user_input = input("Enter words (comma-separated): ")
    return user_input


def open_txt(filepath: str) -> str:
    if not filepath.lower().endswith(".txt"):
        raise ValueError(f"File must be a .txt file, got: {filepath}")
    with open(filepath, encoding="utf-8") as f:
        return f.read()


def ask_for_file() -> str:
    while True:
        path = Prompt.ask("Provide a path to the words.txt file: ").strip()
        try:
            return open_txt(path)
        except FileNotFoundError:
            console.print("That file was not found. Try again.")
        except ValueError:
            console.print("That is not a .txt file. Try again.")


def load_txt(default_path: str = "words.txt") -> str:
    try:
        return open_txt(default_path)
    except (FileNotFoundError, ValueError):
        console.print(f"Didn't find a valid .txt file at {default_path}")
        return ask_for_file()


def word_input() -> str:
    input_type = choose_input_format()
    if input_type == "load_txt":
        words = load_txt()
    else:
        words = manual_words_input()

    normalized_words, _ = normalize_words(words)
    return normalized_words


def check_word_limit(words_input):
    if len(words_input) > 100:
        console.print(
            "[b]Too many words (>100)[/b]. Batched processing not yet supported."
            "\nConsider smaller set of words and try again"
        )
        if not Confirm.ask("Enter the new set?", default=True):
            print("Exiting...")
            raise SystemExit(0)
        else:
            main()  # recursion is love, recursion is life


def main(output_dir: str = "mp3s", failed: list = ()):

    provider, provider_class, env_var = choose_provider()
    if not check_api_key(provider, env_var):
        user_api: str | None = None
        console.print("\n[bold]No API key found[/bold]")
        if reprint_intro():
            main()
        else:
            user_api = user_api_input(provider, env_var)
    else:
        user_api = os.getenv("MW_API_KEY")
    if not failed:
        words = word_input()
        validate_path(output_dir)
    else:
        words = failed

    check_word_limit(words)

    fetcher = provider_class(output_dir=output_dir)
    fetcher.run(words=words, api=user_api)

    if fetcher.failed:
        reattempt_folder: str = "downloads/failed_reattempts"
        failed_words: list = fetcher.failed
        prompt = Confirm.ask(
            "\nWould you like to re-fetch failed words from another source?",
            default=True,
        )
        if prompt:
            main(output_dir=reattempt_folder, failed=failed_words)


if __name__ == "__main__":
    continue_running = True
    while continue_running:
        try:
            main()
            console.print("[bold]Program finished[/bold]")
            x = input("\nPress enter to restart or 'q' to exit: ")
            continue_running = x.lower() not in exit_responses
        except KeyboardInterrupt:
            print("\nExiting...")
            exit(0)
        except NotADirectoryError as e:
            logger.error(f"(Output path) {e}")
            console.print(
                "\n[red]Error: Somehow, default output directory is not a directory.[/red]"
                "\nAborting the operation."
            )
            exit(1)
