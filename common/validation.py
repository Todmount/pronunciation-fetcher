import os
import shutil
import string
import re

negative_responses: set = {"no", "n", "nope", "-"}


def validate_path(path) -> None:
    if not os.path.exists(path):
        os.makedirs(path)
        print(f'Created directory: "{path}"')
    if os.path.exists(path) and os.path.isdir(path):
        x = input(
            f'[!] Path "{path}" already exists. Script will clear it. Continue? (Y/n): '
        ).lower()
        if x != negative_responses:
            shutil.rmtree(path)
            os.makedirs(path)
        else:
            print("Aborted by user.")
            exit(0)


def validate_word(word: str) -> str:
    allowed_chars = string.ascii_letters + "-`' "
    if not word:
        return "empty"
    if word.isnumeric():
        return "numeric"
    if not all(char in allowed_chars for char in word):
        return "invalid characters"
    return "valid"


def normalize_words(user_input: str) -> list[str]:
    seen = set()
    words = [word.strip().lower() for word in user_input.split(",")]
    words = [word for word in words if word]
    words = [re.sub(pattern=r"\s+", repl=" ", string=word) for word in words]
    words = [word for word in words if word not in seen and not seen.add(word)]
    return words
