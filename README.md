<h1 align="center">Pronunciation Fetcher</h1>

<p align="center">
  <a href="https://git.io/typing-svg">
    <img src="https://readme-typing-svg.herokuapp.com?font=Jetbrains+Mono&weight=500&duration=5250&pause=1250&color=C1FFD2DA&center=true&vCenter=true&width=600&lines=Fetch+pronunciation+audio+for+your+ANKI+cards" alt="Typing SVG" />
  </a>
</p>

<h2 align="center">📖 Overview </h2> 

<p>
Pronunciation Fetcher fetches US pronunciation audio files from various dictionary sources (see <a href="#available-sources">Available sources</a>). Designed as a component for a future Anki flashcard workflow, it helps language learners access high-quality audio for vocabulary cards.
</p>
 
<h2 align="center">✨ Features</h2>

- 🎯 Downloads US pronunciation audio in OGG/MP3 formats
- 🚀 Batch processing of multiple words with real-time progress reporting
- 📁 Automatic directory management
- 🛡️ Robust error handling with detailed success/failure feedback

<h2 align="center">🚀 Quick Start</h2>

### Prerequisites

- Python 3.12 or higher
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Todmount/pronunciation_audio_scrapper.git
   cd pronunciation_audio_scrapper
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Usage

Run the script and follow the interactive prompts:

```shellsession
foo@bar:~$ python3 get_audio.py

Enter words (comma-separated): dog, cat, mouse
Fetching Free Dictionary API...
[!] Found files in "downloads". Clear them? (Y/n): y
Processing words... 100%
[!] Some words failed. Show details? (Y/n): y
| Word  | Reason          |
|-------|-----------------|
| mouse | Audio not found |

```

In case of failed words, you will be prompted to use another source:

```shellsession
Would you like to re-fetch failed words from another source? (Y/n): y
Created directory: "downloads/failed_reattempts"
Scraping Oxford Learner's Dictionary...
Processing words... 100%
[+] All words fetched successfully!
```

<h2 align="center">📈 Roadmap</h2>

- [x] Implement Free Dictionary API fetching
- [ ] Implement Merriam-Webster API fetching
- [ ] Enact caching
- [ ] Learn packaging

<h2 align="center">🤝 Affiliations & Credits</h2>

<p align="center">
  <!-- Anki -->
  <a href="https://apps.ankiweb.net/">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Anki-icon.svg/240px-Anki-icon.svg.png" height="70">
  </a>
  &nbsp; <!-- for similar spacing -->
  <!-- Merriam-Webster -->
  <!-- <a href="https://www.merriam-webster.com/">
    <img src="https://dictionaryapi.com/images/info/branding-guidelines/MWLogo_DarkBG_120x120_2x.png" height="70">
  </a> 
  &nbsp;&nbsp;&nbsp; -->
  <!-- Oxford -->
  <a href="https://www.oxfordlearnersdictionaries.com/">
    <img src="https://librum.io/wp-content/uploads/2024/06/oxfordlearnersdictionaries-300x300.png.webp" height="70">
  </a>
</p>

<details markdown="1" id=disclaimer><summary>Disclaimer</summary>
  
> *Audio scraped from <b>Oxford Learner’s Dictionary</b> (unofficial, not affiliated with Oxford Languages)   
> **Designed for use with Anki. This project is independent and not affiliated with the official Anki project.

</details>

<details markdown="1" id=available-sources>
  <summary>Available sources</summary>
  <ul>
    <li><a href="https://dictionaryapi.dev/">Free Dictionary API</a></li>
    <li><a href="https://www.oxfordlearnersdictionaries.com/">Oxdord Learner's Dictionary</a></li>
    <!-- <li><a href="https://dictionaryapi.com/">Merriam-Webster Dictionary API</a></li> -->
  </ul>
</details>
