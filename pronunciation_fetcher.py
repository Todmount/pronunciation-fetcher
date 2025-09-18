import os
import logging

from typing import Any
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

providers_dict = {
    "Merriam-Webster API": {
        "specs": {
            "class": MerriamWebsterDictAPIFetcher,
            "env": "MW_API_KEY",
            "url": "https://dictionaryapi.com/",
        },
    },
    "Free Dictionary API": {
        "specs": {"class": FreeDictAPIFetcher},
    },
    "Oxford Learner's Dictionary (Scraper)": {
        "specs": {"class": OxfordDictScraper},
    },
}

needs_api = ["Merriam-Webster API"]


def print_divider(symbol: str = "-", quantity: int = 80) -> None:
    console.print(symbol * quantity)


def next_action_if_api() -> str | None:
    choices = ["1", "2", "exit", "q"]
    console.print("\n[bold]What would you like to do?[/bold]")
    console.print("  1: [cyan]Choose another source[/cyan]")
    console.print("  2: [cyan]Enter API key[/cyan]")
    console.print("  q: Exit the program")
    prompt = Prompt.ask("Enter choice", choices=choices, show_choices=False)
    console.print()  # separator
    if prompt in ["exit", "q"]:
        exit(0)
    elif prompt == "1":
        return "reprint"
    elif prompt == "2":
        return "enter_api"
    else:  # rich.console wouldn't allow it, but PyCharm keep marking its absence as a warning
        return None  # to satisfy PyCharm's static analysis


def user_api_input(provider: str, env_var: str) -> str:
    api_key = Prompt.ask(f"Enter {provider} key")
    with open(".env", "w") as f:
        f.write(f"{env_var}={api_key}")
    return api_key


def api_key_requirement(provider: str) -> bool:
    if provider in needs_api:
        logger.info("API key is required for this source.")
        return True
    else:
        logger.info("No API key required for this source.")
        return False


def get_user_api(provider) -> str | None:
    user_api = os.getenv(providers_dict[provider]["specs"].get("env"))
    if user_api is None:
        console.print("\n[bold]No API key found[/bold]")
        console.print(
            f"You can get one here: {providers_dict[provider]['specs'].get("url")}"
        )
    return user_api


def choose_provider() -> tuple[str, type[AudioPipeline], str]:
    console.print("[b]Choose a provider:[/b]")
    providers_enumerated: dict = {
        i: provider_name
        for i, provider_name in enumerate(providers_dict.keys(), start=1)
    }

    for i, provider_name in providers_enumerated.items():
        console.print(f"  {i}: [cyan]{provider_name}[/cyan]")
    console.print("  q: Exit the program")

    valid_choices: list[str] = [str(i) for i in providers_enumerated.keys()]
    valid_choices.extend(exit_responses)

    user_choice_str = Prompt.ask(
        "\nEnter choice", choices=valid_choices, show_choices=False
    )

    if user_choice_str in exit_responses:
        print("Exiting...")
        exit(0)

    selected_provider = providers_enumerated[int(user_choice_str)]
    selected_class = providers_dict[selected_provider]["specs"].get("class")
    selected_env = providers_dict[selected_provider]["specs"].get("env")

    print_divider()
    console.print(f"Selected: [green]{selected_provider}[/green]")
    return selected_provider, selected_class, selected_env


def choose_input_format() -> str:
    console.print("How would you like to provide words?")
    console.print("  1: Type them directly in the terminal")
    console.print("  2: Load them from a .txt file")
    console.print("  q: Exit the program")

    valid_choices = ["1", "2"]
    valid_choices.extend(exit_responses)

    user_choice = Prompt.ask(
        "\nEnter choice", choices=valid_choices, show_choices=False, default="2"
    )
    print_divider()
    if user_choice == "1":
        return "manual"
    elif user_choice == "2":
        return "load_txt"
    else:
        print("Exiting...")
        exit(0)


def manual_words_input() -> str:
    user_input = console.input("Enter words (comma-separated): ")
    while not user_input:
        if not Confirm.ask("Input is empty. Enter again?", default="True"):
            print("Exiting...")
            exit(0)
        user_input = console.input("Enter words (comma-separated): ")
    return user_input


def open_txt(filepath: str) -> str:
    if not filepath.lower().endswith(".txt"):
        raise ValueError(f"File must be a .txt file, got: {filepath}")
    with open(filepath, encoding="utf-8") as f:
        return f.read()


def ask_for_file() -> str | None:
    """Continuously ask for the path to .txt with words to process"""
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
        console.print("[i]Looking for the 'words.txt'...[/i]")
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

    # unpacking, because normalization returns both valid and invalid lists
    normalized_words, _ = normalize_words(words)
    return normalized_words


def check_word_limit(words_input) -> bool:
    if len(words_input) > 100:
        return False
    else:
        return True


def save_failed_to_txt(output_folder: str, failed_words: list, provider: str) -> None:
    choice = Confirm.ask(
        "Would you like to save failed words into .txt?", default=False
    )
    if choice:
        try:
            with open(f"{output_folder}/FAILED.txt", "a") as f:
                f.write(f"Provider: {provider}\n")
                for i in failed_words:
                    f.write(f"{i}\n")
            console.print(
                f'Failed words saved successfully to "{output_folder}/FAILED.txt"'
            )
        except IOError as e:
            logger.error(
                f"Failed to save the txt file with with failed words.\nReason: {e}"
            )
            console.print(f"Failed to save txt file. Reason: {e}")


def get_setup_info() -> tuple[str, type[AudioPipeline], str, str | None] | None:
    while True:
        provider, provider_class, env_var = choose_provider()
        user_api: str | None = None

        if api_key_requirement(provider):
            user_api = get_user_api(provider)
            if user_api is None:
                next_action = next_action_if_api()
                if next_action == "reprint":
                    continue
                else:
                    user_api = user_api_input(provider, env_var)

        return provider, provider_class, env_var, user_api


def get_words(failed_words: list[str] | None) -> list[str] | None:
    while True:
        if failed_words:
            words_to_process = failed_words
        else:
            words_to_process = word_input()

        if not check_word_limit(words_to_process):
            console.print(
                "[b]Too many words (>100)[/b]. Batched processing not yet supported"
                "\nConsider smaller set of words and try again"
            )
            if not Confirm.ask("Enter the new set?", default=True):
                print("Exiting...")
                exit(0)
            else:
                continue
        return words_to_process


def handle_failed(output_dir, failed_words, provider) -> Any:
    save_failed_to_txt(output_dir, failed_words, provider)
    prompt = Confirm.ask(
        "Would you like to re-fetch failed words from another source?",
        default=True,
    )
    if prompt:
        return True
    else:
        return False


def main(download_folder: str, failed_words: list[str]) -> tuple[str, list[str]]:
    provider, provider_class, env_var, user_api = get_setup_info()
    words_to_process = get_words(failed_words)

    fetcher = provider_class(output_dir=download_folder)
    fetcher.run(words=words_to_process, api=user_api)

    if fetcher.failed:
        failed_words: list[str] = fetcher.failed
        restart = handle_failed(download_folder, failed_words, provider)
        if restart:
            return download_folder, failed_words
    return download_folder, []


if __name__ == "__main__":
    download_folder = "downloads"
    failed_words = []
    validate_path(download_folder)
    while True:
        try:
            print_divider()
            download_folder, failed_words = main(download_folder, failed_words)

            if not failed_words:
                console.print("[bold]Program finished[/bold]")
                print_divider()
                restart_input = console.input("Press enter to restart or 'q' to exit: ")
                if restart_input.lower() in exit_responses:
                    print("Exiting...")
                    exit(0)

        except KeyboardInterrupt:
            print("\nExiting...")
            exit(0)
        except NotADirectoryError as e:
            logger.error(f"[Output path error] {e}")
            console.print(
                "\n[red]Error: Somehow, default output directory is not a directory.[/red]"
                "\nAborting the operation."
            )
            exit(1)
        except IOError as e:
            console.print(f"[!] An error occurred while writing the file: {e}")
