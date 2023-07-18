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

[![Releases](https://img.shields.io/github/v/release/realshouzy/YTDownloader?include_prereleases&label=Latest%20Release)](https://github.com/realshouzy/YTDownloader/releases)
[![Release Downloads](https://img.shields.io/github/downloads/realshouzy/YTDownloader/total)](https://github.com/realshouzy/YTDownloader/releases)
[![Code Size](https://img.shields.io/github/languages/code-size/realshouzy/YTDownloader)](https://github.com/realshouzy/YTDownloader)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20|%203.11-blue.svg)](https://www.python.org/downloads)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/realshouzy/YTDownloader/blob/main/LICENSE)

</div>

<br />

## Info

This project is mostly finished and technically archived, meaning I probably won't add any new features. Although, if necessary, I will fix bugs and other issues.
Additionally, if someone wants to contribute to this project, any [pull request](https://github.com/realshouzy/YTDownloader/pulls) is welcome.

## Disclaimer

This concept is **not** my idea. I was inspired by **[Clear Code]** from this **[Video]**.
I took the liberty to add some features, such as downloading playlists, selecting a download directory and other adjustments and improvements.
You can find the orignial code [here](https://pastebin.com/gRtcAv5c).

The [icon](assets/YTDownloader.ico) can be found [here](https://imgs.search.brave.com/-YtNT5BoWqxmDjwakgEUWH1MDX6wkgY4psWSZt5BzY4/rs:fit:512:512:1/g:ce/aHR0cHM6Ly9jZG4u/aWNvbi1pY29ucy5j/b20vaWNvbnMyLzEz/ODEvUE5HLzUxMi95/b3V0dWJlZGxfOTM1/MjkucG5n).

**WARNING: DOWNLOADING COPYRIGHTED MATERIAL IS HIGHLY ILLEGAL! I DO NOT TAKE ANY RESPONSIBILITY FOR YOUR USAGE OF THIS TOOL!**

Note that ``pytube`` occasionally shows some issues with downloading playlists.

## Download

- For Windows just download the executable [here](https://github.com/realshouzy/YTDownloader/releases)
- For Linux or macOS download the source code, install the [requirements](requirements.txt) via pip and run [main.py](scripts/main.py) in the scripts module

(If you want the latest version, download the source code directly as releases can be delayed.)

## Running the Program

### Requirements

Make sure you have Python 3.10 or higher installed.

The used libraries are:

```python
# standard library
import abc
import concurrent.futures
import pathlib
import re
import typing
import webbrowser

# third party
import PySimpleGUI
import pytube
```

### On Windows

Just run the executable.

### On Linux or macOS

```bash
git clone https://github.com/realshouzy/YTDownloader.git
pip install -r requirements.txt
python3 /script/main.py
```

## Tutorial

### Video

1. Step:

- Copy and paste the link into the input field
- It will automatically detected that it is a YouTube video
 ![video_step1](/assets/Video/step1.png)

<br />

2. Step:

- Press "submit" amd wait for a new window to pop up.
- This windows has two taps. The first one contains information about the video.
 ![video_step2](/assets/Video/step2.png)

<br />

3. Step:

- Click the "download" tap. This tap contains the download options.
 ![video_step3](/assets/Video/step3.png)

<br />

4. Step:

- Click "browse" or directly type in the directory you want the vidoe to be saved in.
 ![video_step4](/assets/Video/step4.png)

<br />

5. Step:

- Now decide which download option you want and click the "Download" button.
- You can see the download progress in the progress bar below.
 ![video_step5](/assets/Video/step5.png)

<br />

6. Step:

- When the download has finished, a window will pop up to notify you. <br />
 ![video_step6](/assets/Video/step6.png)

7. Step:

- Enjoy the video!

<br />
<br />

### Playlist

1. Step:

- Copy and paste the link into the input field
- It will automatically detected that it is a YouTube playlist
 ![playlist_step1](/assets/Playlist/step1.png)

<br />

2. Step:

- Press "submit" amd wait for a new window to pop up (this can take some time, since pytube is not the fastest).
- This window has two taps. The first one contains information about the playlist.
 ![playlist_step2](/assets/Playlist/step2.png)

<br />

3. Step:

- Click the "download" tap. This tap contains the download options.
 ![playlist_step3](/assets/Playlist/step3.png)

<br />

4. Step:

- Click "browse" or directly type in the directory you want the vidoe to be saved in.
 ![playlist_step4](/assets/Playlist/step4.png)

<br />

5. Step:

- Now decide which download option you want and click the "Download" button.
- You can see the download progress in the progress bar below.
 ![playlist_step5](/assets/Playlist/step5.png)

<br />

6. Step:

- When the download has finished, a window will pop up to notify you. <br />
 ![playlist_step6](/assets/Playlist/step6.png)

7. Step:

- A new folder with the name of the playlist will be created in the directory you submited.
- The video will be in that folder.
- Enjoy the videos!

[Clear Code]: https://www.youtube.com/channel/UCznj32AM2r98hZfTxrRo9bQ
[Video]: https://youtu.be/QeMaWQZllhg?t=11466
