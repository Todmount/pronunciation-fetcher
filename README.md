<h1 align="center"> 🎵 Pronunciation Audio Scraper </h1>

<!--
> A Python tool for downloading US pronunciation audio files from Oxford Learner's Dictionary -->
<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?lines=Python+tool+for+downloading+pronunciation;Oxford+Learner's+Dictionary;For+ANKI+cards&center=true&width=500&height=45&size=20&duration=4250&pause=1000">
</p>

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📖 Overview 

This tool scrapes US pronunciation audio files (.ogg format) from Oxford Learner's Dictionary. It's designed as a component for a future Anki flashcard creation system, helping language learners access high-quality pronunciation audio for their vocabulary cards.

## ✨ Features

- 🎯 Downloads US pronunciation audio in OGG format
- 🚀 Batch processing of multiple words
- 📁 Automatic directory management
- ⚠️ Comprehensive error handling with detailed feedback
- 📊 Success/failure reporting
- 🛡️ Robust exception handling for network issues

## 🚀 Quick Start

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

```bash
python pronunciation_audio_scrapper.py
```

### Plans
- Add support for other dictionaries
- Discover dictionary API
