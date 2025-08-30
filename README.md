<!--- <h1 align="center" title="Project name"> Pronunciation Fetcher</h1> --->
<p align="center">
  <a href="">
    <img src="https://res.cloudinary.com/dxteec1w4/image/upload/v1756072579/proninciation_fetcher_vue_dark_cdtelr.png" title="Project name" alt="Pronunciation Fetcher" style="width:400px"/>
  </a>
</p>

<!-- Typing animation -->
<p align="center">
  <a href="https://git.io/typing-svg">
    <img src="https://readme-typing-svg.herokuapp.com?font=Jetbrains+Mono&weight=500&duration=5250&pause=1250&color=41b883&center=true&vCenter=true&width=600&lines=Fetch+pronunciation+audio+for+your+ANKI+cards" 
      title="Typing animation" alt="Fetch pronunciation audio for your ANKI cards" />
  </a>
</p>

<!-- Project-specific badges -->
<p align="center">
  <a href="https://python.org" title="Supported python versions">
    <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python 3.12+"></a>
  <a href="LICENSE" title="License">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License - MIT"></a>
  <a href="https://github.com/psf/black" title="Code style">
    <img src="https://img.shields.io/badge/Code%20Style-black-000000.svg" alt="Code style: black"></a>
</p>

<h2 align="left">Overview </h2> 

<p>
  Pronunciation Fetcher fetches US pronunciation audio files from various dictionary sources (see <a href="#available-sources">Available sources</a>). 
  Designed as a component for a future Anki flashcard workflow, it helps language learners access high-quality audio for vocabulary cards
</p>
 
<h2 align="left">Features</h2>

- Downloads US pronunciation audio in MP3 format
- Supports up to 100-word set
- Batch processing of multiple words with real-time progress reporting
- Robust error handling with detailed success/failure feedback

<h2 align="left">Quick Start</h2>

### Prerequisites

- Python 3.12 or higher
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Todmount/pronunciation_audio_scrapper.git
   cd pronunciation_audio_scrapper
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Usage

> #### API key requirements
> If you want to use the [Merriam-Webster Dictionary API](https://dictionaryapi.com/), you must get your own API key from their developer portal
> - You will be prompted to enter your key
> - You can redact the key in a .env file at the project root
> - A .env.example file is provided to show the required format
> ```text
> # .env
> MW_API_KEY=your_api_key_here
> ```

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
All words fetched successfully!
```

<h2 align="left">Roadmap</h2>

- [x] Implement Free Dictionary API fetching
- [x] Implement Merriam-Webster API fetching
- [x] Add .txt words format support
- [ ] Enact caching
- [ ] Package with PyPi

## Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request

## Contact
You could find relevant contact info on my [GitHub profile](https://github.com/Todmount)

<h2 align="left">Affiliations & Credits</h2>

<p align="left">
  <!-- Anki -->
  <a href="https://apps.ankiweb.net/">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Anki-icon.svg/240px-Anki-icon.svg.png" style="height:50px" alt="ANKI" title="ANKI"></a>
  &nbsp; <!-- for similar spacing -->
  <!-- Merriam-Webster -->
  <a href="https://www.merriam-webster.com/">
    <img src="https://dictionaryapi.com/images/info/branding-guidelines/MWLogo_DarkBG_120x120_2x.png" style="height:50px" alt="Merriam-Webster Learner's Dictionary" title="Merriam-Webster Learner's Dictionary"></a> 
  &nbsp;&nbsp;&nbsp;
  <!-- Oxford -->
  <a href="https://www.oxfordlearnersdictionaries.com/">
    <img src="https://librum.io/wp-content/uploads/2024/06/oxfordlearnersdictionaries-300x300.png.webp" style="height:50px" alt="Oxford Learner's Dictionaries" title="Oxford Learner's Dictionaries"></a>
</p>

<details markdown="1" id=disclaimer><summary>Disclaimer</summary>
  <p><sub>
    *Audio scraped from <b>Oxford Learner’s Dictionary</b> (unofficial, not affiliated with Oxford Languages)<br>
    **Designed for use with Anki. This project is independent and not affiliated with the official Anki project
  </sub></p>
</details>

<details markdown="1" id=available-sources>
  <summary>Available sources</summary>
  <ul>
    <li><a href="https://dictionaryapi.dev/">Free Dictionary API</a></li>
    <li><a href="https://www.oxfordlearnersdictionaries.com/">Oxford Learner's Dictionary</a></li>
    <li><a href="https://dictionaryapi.com/">Merriam-Webster Learner's Dictionary API</a></li>
  </ul>
</details>
