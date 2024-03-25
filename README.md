<h1 align = 'center'>
 <img
        src = 'assets/YTdownloader.png'
        height = '100'
        width = '100'
        alt = 'Icon'
    />
    <br>
 YTDownloader
 <br />
 A program to download any YouTube video or playlist
</h1>

<div align = 'center'>

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/realshouzy/YTDownloader/main.svg)](https://results.pre-commit.ci/latest/github/realshouzy/YTDownloader/main)
[![pylint status](https://github.com/realshouzy/YTDownloader/actions/workflows/pylint.yaml/badge.svg)](https://github.com/realshouzy/YTDownloader/actions/workflows/pylint.yaml)
[![tests status](https://github.com/realshouzy/YTDownloader/actions/workflows/tests.yaml/badge.svg)](https://github.com/realshouzy/YTDownloader/actions/workflows/tests.yaml)
[![CodeQL](https://github.com/realshouzy/YTDownloader/actions/workflows/codeql.yml/badge.svg)](https://github.com/realshouzy/YTDownloader/actions/workflows/codeql.yml)
[![Releases](https://img.shields.io/github/v/release/realshouzy/YTDownloader?include_prereleases&label=Latest%20Release)](https://github.com/realshouzy/YTDownloader/releases)
[![semantic-release](https://img.shields.io/badge/%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/realshouzy/YTDownloader/releases)
[![Downloads](https://img.shields.io/github/downloads/realshouzy/YTDownloader/total)](https://github.com/realshouzy/YTDownloader/releases)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10%20|%203.11|%203.12-blue.svg)](https://www.python.org/downloads)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/realshouzy/YTDownloader/blob/main/LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

</div>

<br />

## Disclaimer

**WARNING: DOWNLOADING COPYRIGHTED MATERIAL IS HIGHLY ILLEGAL! I DO NOT TAKE ANY RESPONSIBILITY FOR YOUR USAGE OF THIS TOOL!**

## Tutorial

A tutorial on how to the application works can be found [here](/TUTORIAL.md).

## Running the Program

### Requirements

Make sure you have Python 3.8 or higher installed.

The used libraries are:

```python
# standard library
import concurrent.futures
import pathlib
import re
import typing
import webbrowser

# third party
import PySimpleGUI
import pytube

# for testing
import pytest
```

### On Windows

Simply download the executable [here](https://github.com/realshouzy/YTDownloader/releases/latest) and run it. This is the quickest way to get started.

Alternatively, you can directly run the script by following these steps:

1. Clone the repository:

```bash
git clone https://github.com/realshouzy/YTDownloader.git && cd YTDownloader
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the script:

```bash
python -m YTDownloader
```

Running the script this way ensures you have access to the latest features and updates.

### On Linux or macOS

Unfortunately, there is no pre-built executable for Unix systems, so you'll need to do the whole procedure:

1. Clone the repository:

```bash
git clone https://github.com/realshouzy/YTDownloader.git && cd YTDownloader
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the script:

```bash
python3 -m YTDownloader
```

## Regarding the lack of tests

While this project currently lacks tests, I acknowledge the importance of testing for ensuring code quality and reliability is. Initially, due to my limited knowledge when starting the project, I didn't prioritize writing tests. As the project evolved, I didn't care to invest time in writing tests, as I originally intended it to be a smaller-scale project. Recognizing the significance of testing in continuous integration, I have taken the initiative to write tests.

## Contributing

If you are interested in contributing to this project, please refer [here](/CONTRIBUTING.md) for more information .

## License

``YTDownloader`` is available under the [MIT license](/LICENSE)

## Credit

This concept is **not** my idea. I was inspired by **Clear Code** from [this idea](https://github.com/clear-code-projects/PySimpleGuiUltimate/blob/main/youtube.py).
I took the liberty to add some features and extend the code base, such as downloading playlists, selecting a download directory and other adjustments and improvements.

The [icon](assets/YTDownloader.ico) can be found [here](https://imgs.search.brave.com/-YtNT5BoWqxmDjwakgEUWH1MDX6wkgY4psWSZt5BzY4/rs:fit:512:512:1/g:ce/aHR0cHM6Ly9jZG4u/aWNvbi1pY29ucy5j/b20vaWNvbnMyLzEz/ODEvUE5HLzUxMi95/b3V0dWJlZGxfOTM1/MjkucG5n).
