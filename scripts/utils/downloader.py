#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module containing all classes to download YouTube content."""
from __future__ import annotations

import re
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any, Optional

import PySimpleGUI as sg
import pytube.exceptions
from pytube import Playlist, YouTube

from .download_options import AUDIO, HD, LD
from .downloader_base import YouTubeDownloader

if TYPE_CHECKING:
    from pathlib import Path

    from pytube import Stream

    from .download_options import DownloadOptions

__all__: list[str] = ["PlaylistDownloader", "VideoDownloader", "get_downloader"]


def get_downloader(url: str) -> PlaylistDownloader | VideoDownloader:
    """Helper function that returns the appropriate YouTube downloader based on the given url.

    :param str url: YouTube url
    :return PlaylistDownloader|VideoDownloader: PlaylistDownloader or VideoDownloader
    """
    youtube_playlist_pattern: re.Pattern[str] = re.compile(
        r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))\/playlist\?list=([0-9A-Za-z_-]{34})",
    )
    youtube_video_pattern: re.Pattern[str] = re.compile(
        r"(?:https?:\/\/)?(?:www\.)?youtu\.?be(?:\.com)?\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)([\w\-_]+)\&?",
    )

    if re.fullmatch(youtube_playlist_pattern, url):
        return PlaylistDownloader(url)
    if re.fullmatch(youtube_video_pattern, url):
        return VideoDownloader(url)
    raise pytube.exceptions.RegexMatchError(
        "get_downloader",
        "youtube_video_pattern or youtube_playlist_pattern",
    )


# pylint: disable=attribute-defined-outside-init, unused-argument


class PlaylistDownloader(YouTubeDownloader):
    """Class that contains and creates the window and necessary methods to download a YouTube playlist."""

    __slots__: tuple[str, ...] = (
        "url",
        "playlist",
        "select_dict",
        "download_window",
        "folder",
    )

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.playlist: Playlist = Playlist(self.url)

        # binding the playlists (list of streams) to corresponding download option
        hd_list: list[Optional[Stream]] = self.get_playlist(HD)
        ld_list: list[Optional[Stream]] = self.get_playlist(LD)
        audio_list: list[Optional[Stream]] = self.get_playlist(AUDIO)
        self.select_dict: dict[DownloadOptions, Optional[list[Stream]]] = {  # type: ignore
            HD: hd_list if None not in hd_list else None,
            LD: ld_list if None not in ld_list else None,
            AUDIO: audio_list if None not in audio_list else None,
        }

        # defining layouts
        info_tab: list[list[sg.Text]] = [
            [sg.Text("URL:"), sg.Text(self.url, enable_events=True, key="-URL-")],
            [sg.Text("Title:"), sg.Text(self.playlist.title)],
            [sg.Text("Videos:"), sg.Text(self.playlist.length)],  # type: ignore
            [sg.Text("Views:"), sg.Text(f"{self.playlist.views:,}")],
            [
                sg.Text("Owner:"),
                sg.Text(self.playlist.owner, enable_events=True, key="-OWNER-"),
            ],
            [sg.Text("Last updated:"), sg.Text(self.playlist.last_updated)],
        ]

        download_all_tab: list[list[sg.Text | sg.Input | sg.Frame]] = [
            [
                sg.Text("Download Folder"),
                sg.Input(size=(53, 1), enable_events=True, key="-FOLDER-"),
                sg.FolderBrowse(),
            ],
            [
                sg.Frame(
                    "Highest resolution",
                    [
                        [
                            sg.Button("Download All", key="-HD-"),
                            sg.Text(HD.resolution),  # type: ignore
                            sg.Text(self.get_playlist_size(HD)),
                        ],
                    ],
                ),
            ],
            [
                sg.Frame(
                    "Lowest resolution",
                    [
                        [
                            sg.Button("Download All", key="-LD-"),
                            sg.Text(LD.resolution),  # type: ignore
                            sg.Text(self.get_playlist_size(LD)),
                        ],
                    ],
                ),
            ],
            [
                sg.Frame(
                    "Audio only",
                    [
                        [
                            sg.Button("Download All", key="-AUDIOALL-"),
                            sg.Text(self.get_playlist_size(AUDIO)),
                        ],
                    ],
                ),
            ],
            [sg.VPush()],
            [
                sg.Text(
                    "",
                    key="-COMPLETED-",
                    size=(57, 1),
                    justification="c",
                    font="underline",
                ),
            ],
            [
                sg.Progress(
                    self.playlist.length,
                    orientation="h",
                    size=(20, 20),
                    key="-DOWNLOADPROGRESS-",
                    expand_x=True,
                    bar_color="Black",
                ),
            ],
        ]

        main_layout: list[list[sg.TabGroup]] = [
            [
                sg.TabGroup(
                    [
                        [
                            sg.Tab("info", info_tab),
                            sg.Tab("download all", download_all_tab),
                        ],
                    ],
                ),
            ],
        ]

        self.download_window: sg.Window = sg.Window(
            "Youtube Downloader",
            main_layout,
            modal=True,
        )

    def get_playlist(self, download_options: DownloadOptions) -> list[Optional[Stream]]:
        """Returns a list of the streams to the corresponding download option by using threads."""
        args: tuple[tuple[YouTube, DownloadOptions], ...] = tuple(
            zip(
                self.playlist.videos,
                (download_options,) * self.playlist.length,
                strict=True,
            ),
        )

        with ThreadPoolExecutor() as executor:
            stream_list: list[Optional[Stream]] = list(
                executor.map(
                    lambda args: self.get_stream_from_video(*args),
                    args,
                ),
            )
        return stream_list

    def get_playlist_size(self, download_options: DownloadOptions) -> str:
        """Returns the size of the playlist to the corresponding download option."""
        stream_selections: Optional[list[Stream]] = self.select_dict[download_options]
        if stream_selections is None:
            return "Unavailable"
        return f"{round(sum(video.filesize for video in stream_selections) / 1048576, 1)} MB"

    def create_window(self) -> None:
        # download window event loops
        while True:
            event, values = self.download_window.read()  # type: ignore
            try:
                self.folder: str = values["-FOLDER-"]
            except TypeError:
                break

            if event == sg.WIN_CLOSED:
                break

            if event == "-URL-":
                webbrowser.open(self.url)

            if event == "-OWNER-":
                webbrowser.open(self.playlist.owner_url)

            if event == "-HD-":
                self.download(HD)

            if event == "-LD-":
                self.download(LD)

            if event == "-AUDIOALL-":
                self.download(AUDIO)

        self.download_window.close()

    def download(self, download_options: DownloadOptions) -> None:
        if self.select_dict[download_options] is None:
            self.resolution_unavailable_popup()
            return

        if not self.folder:
            self.download_dir_popup()
            return

        download_dir: Path = self.increment_dir_name(
            self.folder,
            self.remove_forbidden_characters(self.playlist.title),
        )

        download_counter: int = 0
        for video in self.select_dict[download_options]:  # type: ignore
            video.download(
                output_path=str(download_dir),
                filename=f"{self.remove_forbidden_characters(video.title)}.mp4",
            )
            download_counter += 1
            self.download_window["-DOWNLOADPROGRESS-"].update(download_counter)  # type: ignore
            self.download_window["-COMPLETED-"].update(
                f"{download_counter} of {self.playlist.length}",  # type: ignore
            )
        self._download_complete()

    def _download_complete(self) -> None:
        """Helper method that resets the download progressbar and notifies the user when the download has finished."""
        self.download_window["-DOWNLOADPROGRESS-"].update(0)  # type: ignore
        self.download_window["-COMPLETED-"].update("")  # type: ignore
        sg.Popup("Download completed")


class VideoDownloader(YouTubeDownloader):
    """Class that contains and creates the window and necessary methods to download a YouTube video."""

    __slots__: tuple[str, ...] = (
        "url",
        "video",
        "select_dict",
        "download_window",
        "folder",
    )

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self.video: YouTube = YouTube(
            self.url,
            on_progress_callback=self._progress_check,
            on_complete_callback=self._on_complete,
        )

        # binding videos to corresponding download option
        self.select_dict: dict[DownloadOptions, Optional[Stream]] = {
            HD: self.get_stream_from_video(self.video, HD),
            LD: self.get_stream_from_video(self.video, LD),
            AUDIO: self.get_stream_from_video(self.video, AUDIO),
        }

        # defining layouts
        info_tab: list[list[sg.Text | sg.Multiline]] = [
            [sg.Text("URL:"), sg.Text(self.url, enable_events=True, key="-URL-")],
            [sg.Text("Title:"), sg.Text(self.video.title)],
            [sg.Text("Length:"), sg.Text(f"{round(self.video.length / 60,2)} minutes")],
            [sg.Text("Views:"), sg.Text(f"{self.video.views:,}")],
            [
                sg.Text("Creator:"),
                sg.Text(self.video.author, enable_events=True, key="-CREATOR-"),
            ],
            [
                sg.Text("Thumbnail:"),
                sg.Text(self.video.thumbnail_url, enable_events=True, key="-THUMB-"),
            ],
            [
                sg.Text("Description:"),
                sg.Multiline(
                    self.video.description,
                    size=(40, 20),
                    no_scrollbar=True,
                    disabled=True,
                ),
            ],
        ]

        download_tab: list[
            list[sg.Text | sg.Input | sg.Button]
            | list[sg.Text | sg.Input | sg.Frame | sg.Progress]
        ] = [
            [
                sg.Text("Download Folder"),
                sg.Input(size=(27, 1), enable_events=True, key="-FOLDER-"),
                sg.FolderBrowse(),
            ],
            [
                sg.Frame(
                    "Highest resolution",
                    [
                        [
                            sg.Button("Download", key="-HD-"),
                            sg.Text(HD.resolution),  # type: ignore
                            sg.Text(self.get_video_size(HD)),
                        ],
                    ],
                ),
            ],
            [
                sg.Frame(
                    "Lowest resolution",
                    [
                        [
                            sg.Button("Download", key="-LD-"),
                            sg.Text(LD.resolution),  # type: ignore
                            sg.Text(self.get_video_size(LD)),
                        ],
                    ],
                ),
            ],
            [
                sg.Frame(
                    "Audio only",
                    [
                        [
                            sg.Button("Download", key="-AUDIO-"),
                            sg.Text(self.get_video_size(AUDIO)),
                        ],
                    ],
                ),
            ],
            [sg.VPush()],
            [
                sg.Text(
                    "",
                    key="-COMPLETED-",
                    size=(40, 1),
                    justification="c",
                    font="underline",
                ),
            ],
            [
                sg.Progress(
                    100,
                    orientation="h",
                    size=(20, 20),
                    key="-DOWNLOADPROGRESS-",
                    expand_x=True,
                    bar_color="Black",
                ),
            ],
        ]

        main_layout: list[list[sg.TabGroup]] = [
            [
                sg.TabGroup(
                    [[sg.Tab("info", info_tab), sg.Tab("download", download_tab)]],
                ),
            ],
        ]

        self.download_window: sg.Window = sg.Window(
            "Youtube Downloader",
            main_layout,
            modal=True,
        )

    def get_video_size(self, download_options: DownloadOptions) -> str:
        """Returns the size of the video to the corresponding download option."""
        stream_selection: Optional[Stream] = self.select_dict[download_options]
        if stream_selection is None:
            return "Unavailable"
        return f"{round(stream_selection.filesize / 1048576, 1)} MB"

    def create_window(self) -> None:
        # download window event loop
        while True:
            event, values = self.download_window.read()  # type: ignore
            try:
                self.folder = values["-FOLDER-"]
            except TypeError:
                break

            if event == sg.WIN_CLOSED:
                break

            if event == "-URL-":
                webbrowser.open(self.url)

            if event == "-CREATOR-":
                webbrowser.open(self.video.channel_url)

            if event == "-THUMB-":
                webbrowser.open(self.video.thumbnail_url)

            if event == "-HD-":
                self.download(HD)

            if event == "-LD-":
                self.download(LD)

            if event == "-AUDIO-":
                self.download(AUDIO)

        self.download_window.close()

    def download(self, download_options: DownloadOptions) -> None:
        if self.select_dict[download_options] is None:
            self.resolution_unavailable_popup()
            return

        if not self.folder:
            self.download_dir_popup()
            return
        (
            self.select_dict[download_options].download(  # type: ignore
                output_path=self.folder,
                filename=f"{self.increment_file_name(self.folder, self.remove_forbidden_characters(self.video.title))}.mp4",
            )
        )

    def _progress_check(
        self,
        stream: Any,
        chunk: bytes,
        bytes_remaining: int,
    ) -> None:  # parameters are necessary
        """Helper method that updated the progress bar when progress in the video download was made."""
        self.download_window["-DOWNLOADPROGRESS-"].update(
            100 - round(bytes_remaining / stream.filesize * 100),  # type: ignore
        )
        self.download_window["-COMPLETED-"].update(
            f"{100 - round(bytes_remaining / stream.filesize * 100)}% completed",  # type: ignore
        )

    def _on_complete(
        self,
        stream: Any,
        file_path: Optional[str],
    ) -> None:  # parameters are necessary
        """Helper method that resets the progress bar when the video download has finished."""
        self.download_window["-DOWNLOADPROGRESS-"].update(0)  # type: ignore
        self.download_window["-COMPLETED-"].update("")  # type: ignore
        sg.Popup("Download completed")
        sg.Popup("Download completed")
