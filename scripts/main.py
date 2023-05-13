#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Main module."""
from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import PySimpleGUI as sg
import pytube.exceptions
from utils.downloader import get_downloader
from utils.error_window import ErrorWindow

if TYPE_CHECKING:
    from utils.downloader import PlaylistDownloader, VideoDownloader

sg.theme("Darkred1")


def main() -> Literal[0, 1]:
    """Runs the program."""
    # defining layouts
    start_layout: list[list[sg.Input | sg.Button]] = [
        [sg.Input(key="-LINKINPUT-"), sg.Button("Submit")],
    ]
    start_window: sg.Window = sg.Window("Youtube Downloader", start_layout)
    exit_code: Literal[0, 1] = 0

    # main event loop
    while True:
        try:
            event, values = start_window.read()  # type: ignore
            if event == sg.WIN_CLOSED:
                break

            if event == "Submit":
                youtube_downloader: PlaylistDownloader | VideoDownloader = (
                    get_downloader(values["-LINKINPUT-"])
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
                key_exce,
                "Video or playlist is unreachable or invalid.",
            ).create()

        except Exception as exce:  # pylint: disable=broad-exception-caught
            ErrorWindow(
                exce,
                "Unexpected error\n"
                f"{exce.__class__.__name__} at line {exce.__traceback__.tb_lineno} of {__file__}: {exce}",  # type: ignore
            ).create()
            exit_code = 1
            break

    start_window.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
