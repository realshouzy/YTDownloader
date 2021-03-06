#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Main module
"""
from __future__ import annotations
import PySimpleGUI as sg
import pytube.exceptions

import re

from downloader import VideoDownloader, PlaylistDownloader, ErrorWindow


sg.theme('Darkred1')


def get_valid_downloader(url: str) -> PlaylistDownloader|VideoDownloader:
    """
    Helper function that validates wether the given url is a vaild YouTube Playlist or Video link and returns the appropriate downloader.

    :param str url: YouTube url
    :return PlaylistDownloader|VideoDownloader: PlaylistDownloader or VideoDownloader
    """
    youtube_playlist_pattern: re.Pattern[str] = re.compile(r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))\/playlist\?list=([0-9A-Za-z_-]{34})')
    youtube_video_pattern: re.Pattern[str] = re.compile(r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/|shorts\/)?)([0-9A-Za-z_-]{11})')

    youtube_patterns: dict[re.Pattern[str], PlaylistDownloader|VideoDownloader] = {
        youtube_playlist_pattern: PlaylistDownloader,
        youtube_video_pattern: VideoDownloader
    }

    for pattern, downloader in youtube_patterns.items():
        if re.search(pattern, url):
            return downloader(url)

    raise pytube.exceptions.RegexMatchError(get_valid_downloader, youtube_patterns)



def main() -> None:
    """
    Runs the program.
    """
    # -------------------- defining layouts
    start_layout = [
        [sg.Input(key='-LINKINPUT-'), sg.Button('Submit')],
    ]
    start_window = sg.Window('Youtube Downloader', start_layout)

    # -------------------- main event loop
    while True:
        try:
            event, values = start_window.read()
            if event == sg.WIN_CLOSED:
                break

            if event == 'Submit':
                youtube_downloader = get_valid_downloader(values['-LINKINPUT-'])
                youtube_downloader.create_window()

        except pytube.exceptions.RegexMatchError as rmx:
            if not values['-LINKINPUT-']:
                ErrorWindow(rmx, 'Please provide link.').create()
            else:
                ErrorWindow(rmx, 'Invalid link.').create()

        except pytube.exceptions.AgeRestrictedError as arx:
            ErrorWindow(arx, 'Video age restriced.').create()

        except pytube.exceptions.VideoPrivate as vpx:
            ErrorWindow(vpx, 'Video is privat.').create()

        except pytube.exceptions.MembersOnly as mox:
            ErrorWindow(mox, 'Video is for members only.').create()

        except pytube.exceptions.VideoRegionBlocked as vgbx:
            ErrorWindow(vgbx, 'Video is block in your region.').create()

        except pytube.exceptions.VideoUnavailable as vux:
            ErrorWindow(vux, 'Video Unavailable.').create()

        except Exception as x:
            ErrorWindow(x, 'Unexpected error\n'f'{type(x).__name__} at line {x.__traceback__.tb_lineno} of {__file__}: {x}').create()
            break

    start_window.close()




if __name__ == '__main__':
    main()