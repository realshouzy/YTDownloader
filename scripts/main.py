#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Main module."""
from __future__ import annotations

import re
import PySimpleGUI as sg
import pytube.exceptions

from utils.downloader import VideoDownloader, PlaylistDownloader
from utils.error_window import ErrorWindow


sg.theme("Darkred1")


def get_valid_downloader(url: str) -> PlaylistDownloader | VideoDownloader:
    """Helper function that validates wether the given url is a vaild YouTube Playlist or Video link and returns the appropriate downloader.

    :param str url: YouTube url
    :return PlaylistDownloader|VideoDownloader: PlaylistDownloader or VideoDownloader
    """
    youtube_playlist_pattern: re.Pattern[str] = re.compile(
        r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))\/playlist\?list=([0-9A-Za-z_-]{34})"
    )
    youtube_video_pattern: re.Pattern[str] = re.compile(
        r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/|shorts\/)?)([0-9A-Za-z_-]{11})"
    )

    if re.search(youtube_video_pattern, url):
        return VideoDownloader(url)
    if re.search(youtube_playlist_pattern, url):
        return PlaylistDownloader(url)
    raise pytube.exceptions.RegexMatchError(
        "get_valid_downloader", "youtube_video_pattern or youtube_playlist_pattern"
    )


def main() -> None:
    """Runs the program."""
    # -------------------- defining layouts
    start_layout: list[list[sg.Input | sg.Button]] = [
        [sg.Input(key="-LINKINPUT-"), sg.Button("Submit")],
    ]
    start_window: sg.Window = sg.Window("Youtube Downloader", start_layout)

    # -------------------- main event loop
    while True:
        try:
            event, values = start_window.read()  # type: ignore
            if event == sg.WIN_CLOSED:
                break

            if event == "Submit":
                youtube_downloader: PlaylistDownloader | VideoDownloader = (
                    get_valid_downloader(values["-LINKINPUT-"])
                )
                youtube_downloader.create_window()

        except pytube.exceptions.RegexMatchError as rmx:
            if not values["-LINKINPUT-"]:  # type: ignore
                ErrorWindow(rmx, "Please provide link.").create()
            else:
                ErrorWindow(rmx, "Invalid link.").create()

        except pytube.exceptions.VideoPrivate as vpx:
            ErrorWindow(vpx, "Video is privat.").create()

        except pytube.exceptions.MembersOnly as mox:
            ErrorWindow(mox, "Video is for members only.").create()

        except pytube.exceptions.VideoRegionBlocked as vgbx:
            ErrorWindow(vgbx, "Video is block in your region.").create()

        except pytube.exceptions.VideoUnavailable as vux:
            ErrorWindow(vux, "Video Unavailable.").create()

        except KeyError as key_exce:
            ErrorWindow(
                key_exce, "Video or playlist is unreachable or invalid."
            ).create()

        except Exception as exce:
            ErrorWindow(
                exce,
                "Unexpected error\n"
                f"{exce.__class__.__name__} at line {exce.__traceback__.tb_lineno} of {__file__}: {exce}",  # type: ignore
            ).create()
            break

    start_window.close()


if __name__ == "__main__":
    main()
