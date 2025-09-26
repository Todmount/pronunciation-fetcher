import os
import re
import shutil
import string
import logging

from rich.console import Console
from rich.prompt import Confirm

from common.console_utils import show_separator
from common.constants import CURRENT_DIRECTORY


log = logging.getLogger("pf.validation")
console = Console()


def validate_path(path) -> None:
    full_path = CURRENT_DIRECTORY/path
    log.info(f"Validating path: {full_path}")
    if not os.path.exists(path):
        os.makedirs(path)
        log.info(f"Folder doesn't exist. Creating it...")
    elif os.path.exists(path) and not os.path.isdir(path):
        # log.error(
        #     f"Provided path is not a directory: {full_path}"
        # )  # user reprompted
        # logging for this case handled in the main script
        raise NotADirectoryError(f'Provided path is not a directory')
    elif os.path.isdir(path) and len(os.listdir(path)) != 0:
        # log.debug(f"Downloads folder is not empty: {full_path}")
        log.debug(f"Downloads folder is not empty")
        confirm = Confirm.ask(
            f"Found files in the directory. Clear them?", default=False
        )
        if confirm:
            log.debug("User decided to clear the downloads folder")
            shutil.rmtree(path)
            os.makedirs(path)
        else:
            log.debug("User decided to keep existing files")
    log.info(f"Downloads directory ready!")


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
    log.debug(f"Approximate count of words before normalization: {len(words)}")
    words = [word for word in words if word]
    words = [re.sub(pattern=r"\s+", repl=" ", string=word) for word in words]

    valid_words = []
    invalid_words = []
    show_separator()
    console.print("Normalizing input...")

    for word in words:
        validation_result = validate_word(word)
        if validation_result != "valid":
            console.print(f"Skipping '{word}': {validation_result}")
            invalid_words.append(word)
            continue
        if word not in seen:
            seen.add(word)
            valid_words.append(word)
            
    console.print("Normalization finished!")
    show_separator()
    log.debug(
        f"Normalization complete: {len(valid_words)} valid, {len(invalid_words)} invalid"
    )
    log.debug(
        f"Invalid words: {invalid_words[:10]}{"..." if len(invalid_words)>10 else ""}"
    )

    return valid_words, invalid_words
