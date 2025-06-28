import os
import requests
from bs4 import BeautifulSoup

failed = []

def add_to_failed(word):
    failed.append(word) if word not in failed else failed

def fetch_us_ogg(word: str, output_dir="downloads"):
    # Construct Oxford URL for the word
    word.lower()
    url = f"https://www.oxfordlearnersdictionaries.com/definition/english/{word}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
        ),
        "Referer": "https://www.oxfordlearnersdictionaries.com/",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }

    # Step 1: Fetch the HTML page
    print(f"[🔍] Looking up: {word}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"[✖] Failed to retrieve dictionary page: Status {response.status_code}")
        add_to_failed(word)
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Step 2: Find the US pronunciation .ogg URL
    button = soup.find("div", class_="sound audio_play_button pron-us icon-audio")
    if not button:
        add_to_failed(word)
        print(f"[⚠] No US pronunciation button found for: {word}")
        return

    ogg_url = button.get("data-src-ogg")
    if not ogg_url:
        add_to_failed(word)
        print(f"[⚠] OGG audio not found in page data for: {word}")
        return

    # Ensure full URL
    if ogg_url.startswith("/"):
        ogg_url = "https://www.oxfordlearnersdictionaries.com" + ogg_url

    print(f"[✔] OGG found: {ogg_url}")

    # Step 3: Download the audio file
    try:
        audio_response = requests.get(ogg_url, headers=headers, timeout=10)
        if audio_response.status_code == 200:
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"{word}_us.ogg")
            with open(file_path, "wb") as f:
                f.write(audio_response.content)
            print(f"[💾] Saved to: {file_path}")
        else:
            add_to_failed(word)
            print(f"[✖] Failed to download audio: Status {audio_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[⚠] Error downloading audio: {e}")

if __name__ == "__main__":
    words = ["charming", "chase", "cheek", "cheer", "choir", "chop", "circuit", "civilization", "clarify", "classify", "clerk", "cliff", "clinic", "clip", "coincidence", "collector"]

    for w in words:
        print(f"\nFetching pronunciation for: {w}")
        fetch_us_ogg(w)
    print(f"\nFailed to fetch pronunciation for: {failed}")