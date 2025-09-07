<!--- <h1 align="center" title="Project name"> Pronunciation Fetcher</h1> --->
<p align="center">
  <a href="">
    <img 
        style="width: 500px"
        src="assets/pronunciation_fetcher_vue_dark.webp" 
        title="Project name" 
        alt="Pronunciation Fetcher" 
    /></a>
</p>


<!-- Typing animation 
<div align="center">
  <a href="https://git.io/typing-svg">
    <img src="https://readme-typing-svg.herokuapp.com?font=Jetbrains+Mono&weight=500&duration=5250&pause=1250&color=41b883&center=true&vCenter=true&width=600&lines=Fetch+pronunciation+audio+for+your+ANKI+cards" 
      title="Typing animation" alt="Fetch pronunciation audio for your ANKI cards" />
  </a>
</div> -->


<!-- Project-specific badges -->
<div align="center">
  <a href="https://python.org" title="Supported python versions">
    <img  src="https://img.shields.io/badge/Python-3.12+-blue.svg?&style=flat-square&logo=python" alt="Python 3.12+"></a>
  <a href="LICENSE" title="License">
    <img src="https://img.shields.io/github/license/todmount/pronunciation-fetcher?style=flat-square&label=License&color=%23A6C3A8" alt="License - MIT"></a>
  <a href="https://github.com/psf/black" title="Code style">
    <img src="https://img.shields.io/badge/Code%20style-black-000000.svg?&style=flat-square" alt="Code style: black"></a>
</div>


<details open>
    <summary><h2 align="left">Overview</h2> </summary>
    <div>
      Pronunciation Fetcher fetches US pronunciation audio files from various dictionary sources (see <a href="#available-sources">Available sources</a>). 
      Designed as a component for a future Anki flashcard workflow, it helps language learners access high-quality audio for vocabulary cards
    </div>
</details>


<details open>
    <summary><h2 align="left">Features</h2></summary>
    <ul>
        <li>Downloads US pronunciation audio in MP3 format</li>
        <li>Supports up to 100-word set</li>
        <li>Batch processing of multiple words with real-time progress reporting</li>
        <li>Robust error handling with detailed success/failure feedback</li>
    </ul>
</details>


<details markdown="1">
    <summary><h2 align="left">Quick Start</h2></summary>

### Prerequisites

- Python 3.12 or higher
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Todmount/pronunciation-fetcher.git
   cd pronunciation-fetcher
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
> Certain sources, such as [Merriam-Webster Dictionary API](https://dictionaryapi.com/) require you to get your own API key from their portal
> - **You will be prompted to enter your key before accessing such sources**
> - Additionally, you can manually redact the key in a .env file at the project root
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
</details>


<details open>
    <summary><h2 align="left">Roadmap</h2></summary>

- [x] Implement Free Dictionary API fetching
- [x] Implement Merriam-Webster API fetching
- [x] Add .txt words format support
- [ ] Integrate links to where to get API keys for certain sources
- [ ] Enact caching
- [ ] Package with PyPi

</details>


<details open>
    <summary><h2>Contributing</h2></summary>
    Contributions are welcome! Feel free to open an issue or submit a pull request
</details>


<details open>
    <summary><h2>Contact</h2></summary>
    You could find relevant contact info on my [GitHub profile](https://github.com/Todmount)
</details>


<details open>
    <summary><h2 align="left">Affiliations & Credits</h2></summary>
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
    <details open id=disclaimer><summary>Disclaimer</summary>
      <div><sub>
        *Audio scraped from <b>Oxford Learner’s Dictionary</b> (unofficial, not affiliated with Oxford Languages)<br>
        **Designed for use with Anki. This project is independent and not affiliated with the official Anki project
        <p></p>
      </sub></div>
    </details>
    <details markdown="1" id=available-sources>
      <summary>Available sources</summary>
      <ul>
        <li><a href="https://dictionaryapi.dev/">Free Dictionary API</a></li>
        <li><a href="https://www.oxfordlearnersdictionaries.com/">Oxford Learner's Dictionary</a></li>
        <li><a href="https://dictionaryapi.com/">Merriam-Webster Learner's Dictionary API</a></li>
      </ul>
    </details>
</details>
