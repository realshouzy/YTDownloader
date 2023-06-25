#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Main module."""
from __future__ import annotations

__all__: list[str] = ["main"]

from typing import TYPE_CHECKING, Final, Literal, TypeAlias

import PySimpleGUI as sg
import pytube.exceptions
from utils.downloader import get_downloader
from utils.error_window import create_error_window

if TYPE_CHECKING:
    from utils.downloader import PlaylistDownloader, VideoDownloader

_ExitCode: TypeAlias = Literal[0, 1]

_EXIT_SUCCESS: Final[Literal[0]] = 0
_EXIT_FAILURE: Final[Literal[1]] = 1

sg.theme("Darkred1")


def main() -> _ExitCode:  # pylint: disable=too-many-branches
    """Runs the program."""
    exit_code: _ExitCode = _EXIT_SUCCESS

    # defining layouts
    start_layout: list[list[sg.Input | sg.Button]] = [
        [sg.Input(key="-LINKINPUT-"), sg.Button("Submit")],
    ]
    start_window: sg.Window = sg.Window("Youtube Downloader", start_layout)

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

        except pytube.exceptions.RegexMatchError as re_err:
            if not values["-LINKINPUT-"]:  # type: ignore
                create_error_window(
                    re_err.__class__.__name__,
                    "Please provide link.",
                )
            else:
                create_error_window(re_err.__class__.__name__, "Invalid link.")

        except pytube.exceptions.VideoPrivate as vp_err:
            create_error_window(vp_err.__class__.__name__, "Video is privat.")

        except pytube.exceptions.MembersOnly as mo_err:
            create_error_window(mo_err.__class__.__name__, "Video is for members only.")

        except pytube.exceptions.VideoRegionBlocked as vgb_err:
            create_error_window(
                vgb_err.__class__.__name__,
                "Video is block in your region.",
            )

        except pytube.exceptions.LiveStreamError as ls_err:
            create_error_window(
                ls_err.__class__.__name__,
                "This is an active life stream.",
            )

        except pytube.exceptions.AgeRestrictedError as ar_err:
            create_error_window(
                ar_err.__class__.__name__,
                "This video is age restricted.",
            )

        except pytube.exceptions.VideoUnavailable as vu_err:
            create_error_window(vu_err.__class__.__name__, "Video Unavailable.")

        except KeyError as key_err:
            create_error_window(
                key_err.__class__.__name__,
                "Video or playlist is unreachable or invalid.",
            )

        except Exception as err:  # pylint: disable=broad-exception-caught
            create_error_window(err.__class__.__name__, str(err))
            exit_code = _EXIT_FAILURE
            break

    start_window.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
