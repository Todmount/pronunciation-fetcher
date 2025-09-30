import os

from typing import Any
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt, Confirm
from pathlib import Path
from platformdirs import user_log_path, user_downloads_path

from sources.audio_pipeline import AudioPipeline
from sources.free_dictionary_api import FreeDictAPIFetcher
from sources.merriam_webster_api import MerriamWebsterDictAPIFetcher
from sources.oxford_dictionary_scraper import OxfordDictScraper
from common.validation import normalize_words, validate_path
from common.custom_exceptions import UserExitException
from common.console_utils import show_separator
from common.setup_logger import setup_logger
from common.constants import CURRENT_DIRECTORY

load_dotenv()
console = Console()

appname = "Pronunciation Fetcher"
appauthor = "todmount"
log_path = user_log_path(appname, appauthor)
log = setup_logger(
    name="pf",
    log_file_dir=log_path,
    log_file_name="main.log",
    is_main=True,
)

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
exit_responses: set = {"exit", "q", "quit"}


def next_action_if_api() -> str | None:
    choices = ["1", "2", "exit", "q"]
    console.print("What would you like to do?")
    console.print("  1: Choose another source")
    console.print("  2: Enter API key")
    console.print("  q: Exit the program")
    prompt = Prompt.ask("Enter choice", choices=choices, show_choices=False)
    show_separator()

    if prompt in ["exit", "q"]:
        raise UserExitException
    elif prompt == "1":
        return "reprint"
    else:
        return "enter_api"


def user_api_input(provider: str, env_var: str) -> str:
    api_key = Prompt.ask(f"Enter {provider} key")
    with open(".env", "w") as f:
        f.write(f"{env_var}={api_key}")
    return api_key


def api_key_requirement(provider: str) -> bool:
    if provider in needs_api:
        log.info(f"API key is required: {provider}")
        return True
    else:
        log.debug(f"No API key required: {provider}")

        return False


def get_user_api(provider) -> str | None:
    env_var = providers_dict[provider]["specs"].get("env")
    return os.getenv(env_var) if env_var else None


def choose_provider() -> tuple[str, type[AudioPipeline], str]:
    console.print("Choose a provider:")
    providers_enumerated: dict = {
        i: provider_name
        for i, provider_name in enumerate(providers_dict.keys(), start=1)
    }

    for i, provider_name in providers_enumerated.items():
        console.print(f"  {i}: {provider_name}")

    console.print("  q: Exit the program")

    valid_choices: list[str] = [str(i) for i in providers_enumerated.keys()]
    valid_choices.extend(exit_responses)

    user_choice_str = Prompt.ask(
        "Enter choice", choices=valid_choices, show_choices=False
    )

    if user_choice_str in exit_responses:
        raise UserExitException

    selected_provider = providers_enumerated[int(user_choice_str)]
    selected_class = providers_dict[selected_provider]["specs"].get("class")
    selected_env = providers_dict[selected_provider]["specs"].get("env")
    show_separator()
    
    log.debug(f"Selected provided: {selected_provider}")
    return selected_provider, selected_class, selected_env


def choose_input_format() -> str:
    console.print("How would you like to provide words?")
    console.print("  1: Type them directly in the terminal")
    console.print("  2: Load them from a .txt file")
    console.print("  q: Exit the program")

    valid_choices = ["1", "2"]
    valid_choices.extend(exit_responses)

    user_choice = Prompt.ask(
        "Enter choice", choices=valid_choices, show_choices=False, default="2"
    )
    show_separator()

    if user_choice == "1":
        return "manual"
    elif user_choice == "2":
        return "load_txt"
    else:
        raise UserExitException


def manual_words_input() -> str:
    user_input = console.input("Enter words (comma-separated): ")
    while not user_input:
        if not Confirm.ask("Input is empty. Enter again?", default="True"):
            raise UserExitException
        user_input = console.input("Enter words (comma-separated): ")
    return user_input


def open_txt(filepath: Path) -> str:
    if filepath.suffix != ".txt":
        x = Path(filepath)
        log.debug(f"User attempted to open non-txt file: {x.suffix}")
        raise ValueError(f"File must be a .txt file, got: {filepath}")
    with open(filepath, encoding="utf-8") as f:
        return f.read()


def ask_for_file() -> str | None:
    """Continuously ask for the path to .txt with words to process"""
    while True:
        path = Path(Prompt.ask("Provide a path to the words.txt file").strip())
        try:
            return open_txt(path)
        except FileNotFoundError:
            log.error("That file was not found. Try again.")
        except ValueError:
            log.error("That is not a .txt file. Try again.")


def load_txt(default_path: Path = CURRENT_DIRECTORY / "words.txt") -> str:
    try:
        log.info(f"Looking for the 'words.txt'... at \"{default_path}\"")
        return open_txt(default_path)
    except (FileNotFoundError, ValueError):
        log.error(f"Didn't find a valid .txt file at \"{default_path}\"")
        return ask_for_file()
    except PermissionError:
        log.error(f"User don't have rights to access \"{default_path}\"")
        return ask_for_file()


def word_input() -> str:
    input_type = choose_input_format()
    if input_type == "load_txt":
        log.debug("User decided to provide words as .txt")
        words = load_txt()
    else:
        log.debug("User decided to enter words manually")
        words = manual_words_input()

    # unpacking, because normalization returns both valid and invalid lists
    normalized_words, _ = normalize_words(words)
    return normalized_words


def check_word_limit(words_input) -> bool:
    if len(words_input) > 100:
        log.debug(f"User provided too much words: {len(words_input)}")
        return False
    else:
        return True


def save_failed_to_txt(failed_words: list, provider: str) -> None:
    choice = Confirm.ask(
        "Would you like to export failed words into .txt?", default=False
    )
    if choice:
        log.debug("User decided to export failed words to txt")
        try:
            failed_out_path: Path = log_path / "failed_words.txt"
            with open(failed_out_path, "a") as f:
                f.write(f"Provider: {provider}\n")
                for i in failed_words:
                    f.write(f"{i}\n")

            log.info(f"Failed words exported to \"{failed_out_path}\"")
        except IOError as e:
            console.print(f"Failed to save txt file. Reason: {e}")
    else:
        log.debug("User decided NOT to export failed words to txt")


def get_setup_info() -> tuple[str, type[AudioPipeline], str, str | None] | None:
    while True:
        provider, provider_class, env_var = choose_provider()
        user_api: str | None = None

        if api_key_requirement(provider):
            user_api = get_user_api(provider)
            if user_api is None:
                log.debug(f"No API found for {provider}")
                console.print(
                    f"You can get one here: {providers_dict[provider]['specs'].get("url")}"
                )
                next_action = next_action_if_api()
                if next_action == "reprint":
                    log.debug(f"User decided not to provide the API for {provider}")
                    continue
                else:
                    log.debug(f"User decided to provide API for {provider}")

                    user_api = user_api_input(provider, env_var)

        return provider, provider_class, env_var, user_api


def get_words(failed_words: list[str] | None) -> list[str] | None:
    while True:
        if failed_words:
            words_to_process = failed_words
        else:
            words_to_process = word_input()

        if not check_word_limit(words_to_process):
            log.error(
                "Too many words (>100). Batched processing not yet supported"
                "Consider smaller set of words and try again"
            )
            if not Confirm.ask("Enter the new set?", default=True):
                raise UserExitException
            else:
                continue
        return words_to_process


def handle_failed(failed_words, provider) -> Any:
    save_failed_to_txt(failed_words, provider)
    prompt = Confirm.ask(
        "Would you like to re-fetch failed words from another source?",
        default=True,
    )
    if prompt:
        log.debug("User decided to re-fetch failed words")
        return True
    else:
        log.debug("User decided NOT to re-fetch failed words")
        return False


def get_download_path() -> Path | None:
    user_choice = Confirm.ask("Would you like to change the output path?", default=False)
    if user_choice:
        user_path = Prompt.ask("Provide the new path")
        return Path(user_path)
    return None


def setup_download_path() -> Path:
    default_path = user_downloads_path() / appname
    log.info(f"Current download path is \"{default_path}\"")
    cust_folder = get_download_path()
    if cust_folder:
        download_path = cust_folder
    else:
        download_path = default_path
    validate_path(download_path)
    return download_path


def main(failed_list: list[str], download_path: str | Path) -> tuple[str, list[str]]:
    provider, provider_class, env_var, user_api = get_setup_info()
    words_to_process = get_words(failed_list)
    fetcher = provider_class(output_dir=download_path)
    fetcher.run(words=words_to_process, api=user_api)

    if fetcher.failed:
        failed_list: list[str] = fetcher.failed
        restart = handle_failed(failed_list, provider)
        if restart:
            return download_path, failed_list
    return download_path, []


def run() -> None:
    failed_words = []
    download_folder = setup_download_path()

    while True:
        show_separator()
        download_folder, failed_words = main(failed_words, download_folder)

        if not failed_words:
            console.print("Program finished")
            show_separator()
            restart_input = console.input("Press enter to restart or 'q' to exit: ")
            if restart_input.lower() in exit_responses:
                raise UserExitException
        break


if __name__ == "__main__":
    while True:
        try:
            run()
        except (KeyboardInterrupt, UserExitException):
            log.info("Exiting...")
            exit(0)
        except NotADirectoryError as e:
            log.error(f"{e}")  # user reprompted
            show_separator()
        except IOError as e:
            log.error(f"An error occurred while writing the file: {e}")
