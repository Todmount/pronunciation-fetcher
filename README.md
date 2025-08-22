<h1 align="center"> 🎵 US Pronunciation Audio Scraper </h1>

<p align="center">
> A Python tool for downloading US pronunciation audio files from Oxford Learner's Dictionary
</p>

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


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