#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Main module."""
from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeAlias

import PySimpleGUI as sg
import pytube.exceptions
from utils.downloader import get_downloader
from utils.error_window import create_error_window

if TYPE_CHECKING:
    from utils.downloader import PlaylistDownloader, VideoDownloader

__all__: list[str] = ["main"]

_ExitCode: TypeAlias = Literal[0, 1]

sg.theme("Darkred1")


def main() -> _ExitCode:
    """Runs the program."""
    # defining layouts
    start_layout: list[list[sg.Input | sg.Button]] = [
        [sg.Input(key="-LINKINPUT-"), sg.Button("Submit")],
    ]
    start_window: sg.Window = sg.Window("Youtube Downloader", start_layout)
    exit_code: _ExitCode = 0

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
                create_error_window(rmx, "Please provide link.")
            else:
                create_error_window(rmx, "Invalid link.")

        except pytube.exceptions.VideoPrivate as vpx:
            create_error_window(vpx, "Video is privat.")

        except pytube.exceptions.MembersOnly as mox:
            create_error_window(mox, "Video is for members only.")

        except pytube.exceptions.VideoRegionBlocked as vgbx:
            create_error_window(vgbx, "Video is block in your region.")

        except pytube.exceptions.VideoUnavailable as vux:
            create_error_window(vux, "Video Unavailable.")

        except KeyError as key_exce:
            create_error_window(
                key_exce,
                "Video or playlist is unreachable or invalid.",
            )

        except Exception as exce:  # pylint: disable=broad-exception-caught
            create_error_window(
                exce,
                "Unexpected error\n"
                f"{exce.__class__.__name__} at line {exce.__traceback__.tb_lineno} of {__file__}: {exce}",  # type: ignore
            )
            exit_code = 1
            break

    start_window.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
