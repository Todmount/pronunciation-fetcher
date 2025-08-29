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
    """
    Normalize and validate a comma-separated list of words from user input.

    Processing steps:
        1. Split the input string by commas and lowercase each word.
        2. Strip leading/trailing whitespace and collapse internal multiple spaces.
        3. Remove empty entries.
        4. Validate each word with `validate_word()`.
        5. Collect valid and invalid words into respective lists.
        6. Remove duplicates while preserving the original order.

    Args:
        user_input: Raw string of words separated by commas.

    Returns:
        - A list of valid words (deduplicated, normalized).
        - A list of invalid words (failed validation).
        - An empty list if the input string is empty.
    """
    if not user_input:
        return []
    seen = set()
    words = [word.strip().lower() for word in user_input.split(",")]
    words = [word for word in words if word]
    words = [re.sub(pattern=r"\s+", repl=" ", string=word) for word in words]

    valid_words = []
    invalid_words = []
    console.print("Normalizing input...")
    for word in words:
        if validate_word(word) != "valid":
            logger.warning(f"[!] Skipping '{word}': {validate_word(word)}")
            invalid_words.append(word)
            continue
        if word not in seen:
            seen.add(word)
            valid_words.append(word)

    return valid_words, invalid_words
