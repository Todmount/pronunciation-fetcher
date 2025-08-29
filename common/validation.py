import os
import re
import shutil
import string
import logging
from rich.console import Console
from rich.prompt import Confirm

logger = logging.getLogger(__name__)
console = Console()

negative_responses: set = {"no", "n", "nope", "-"}
positive_responses: set = {"yes", "y", "yeah", "+"}
exit_responses: set = {"exit", "q", "quit"}


def validate_path(path) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
        print(f'Created directory: "{path}"')
    if os.path.exists and not os.path.isdir(path):
        raise NotADirectoryError(f'Path "{path}" is not a directory.')
    if os.path.exists(path) and os.path.isdir(path) and len(os.listdir(path)) != 0:
        confirm = Confirm.ask(
            f'[!] Found files in "{path}". Clear them?', default=False
        )
        if confirm:
            shutil.rmtree(path)
            os.makedirs(path)


def validate_word(word: str) -> str:
    allowed_chars = string.ascii_letters + "-`' "
    if not word:
        return "Is empty"
    if word.isnumeric():
        return "Is numeric"
    if not all(char in allowed_chars for char in word):
        return "Contains invalid characters"
    return "valid"


def normalize_words(user_input: str) -> tuple[list, list] | list:
    if not user_input:
        return []
    seen = set()
    words = [word.strip().lower() for word in user_input.split(",")]
    words = [word for word in words if word]
    words = [re.sub(pattern=r"\s+", repl=" ", string=word) for word in words]

    valid_words = []
    invalid_words = []
    for word in words:
        if validate_word(word) != "valid":
            logger.warning(f"[!] Skipping '{word}': {validate_word(word)}")
            invalid_words.append(word)
            continue
        if word not in seen:
            seen.add(word)
            valid_words.append(word)

    return valid_words, invalid_words
