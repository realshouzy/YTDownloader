# -*- coding: UTF-8 -*-
"""Module containing all classes to download YouTube content."""
from __future__ import annotations
from typing import Any, Optional, Callable
from pathlib import Path

import webbrowser
import PySimpleGUI as sg
from pytube import YouTube, Playlist

from .downloader_base import YouTubeDownloader
from .download_option import DownloadOption


# -------------------- defining download options
LD: DownloadOption = DownloadOption("360p", "video", True, None)
HD: DownloadOption = DownloadOption("720p", "video", True, None)
AUDIO: DownloadOption = DownloadOption(None, "audio", False, "128kbps")


DOWNLOAD_DIR_POPUP: Callable[[], Any] = lambda: sg.Popup(
    "Please select a download directory", title="Info"
)


class PlaylistDownloader(YouTubeDownloader):
    """Class that contains and creates the window and necessary methods to download a YouTube playlist."""

    def __init__(self, url: str) -> None:
        """Initializes PlaylistDownloader instance.

        :param str url: YouTube playlist url
        """
        super().__init__(url)
        self.playlist: Playlist = Playlist(self.url)

        # -------------------- defining layouts
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
                            sg.Text(HD.RESOLUTION),  # type: ignore
                            sg.Text(f"{self.get_playlist_size(HD)} MB"),
                        ]
                    ],
                )
            ],
            [
                sg.Frame(
                    "Lowest resolution",
                    [
                        [
                            sg.Button("Download All", key="-LD-"),
                            sg.Text(LD.RESOLUTION),  # type: ignore
                            sg.Text(f"{self.get_playlist_size(LD)} MB"),
                        ]
                    ],
                )
            ],
            [
                sg.Frame(
                    "Audio only",
                    [
                        [
                            sg.Button("Download All", key="-AUDIOALL-"),
                            sg.Text(f"{self.get_playlist_size(AUDIO)} MB"),
                        ]
                    ],
                )
            ],
            [sg.VPush()],
            [
                sg.Text(
                    "",
                    key="-COMPLETED-",
                    size=(57, 1),
                    justification="c",
                    font="underline",
                )
            ],
            [
                sg.Progress(
                    self.playlist.length,
                    orientation="h",
                    size=(20, 20),
                    key="-DOWNLOADPROGRESS-",
                    expand_x=True,
                    bar_color="Black",
                )
            ],
        ]

        self.main_layout: list[list[sg.TabGroup]] = [
            [
                sg.TabGroup(
                    [
                        [
                            sg.Tab("info", info_tab),
                            sg.Tab("download all", download_all_tab),
                        ]
                    ]
                )
            ]
        ]

        self.download_window: sg.Window = sg.Window(
            "Youtube Downloader", self.main_layout, modal=True
        )

    def get_playlist_size(self, download_option: DownloadOption) -> float:
        """Helper method that calculates the file size of a playlist, since pytube does not have this feature.

        :param DownloadOption option: class containing the download options
        :return float: size of the playlist
        """
        playlist_size: int = sum(
            (
                video.streams.filter(
                    resolution=download_option.RESOLUTION,
                    type=download_option.TYPE,
                    progressive=download_option.PROGRESSIVE,
                    abr=download_option.ABR,
                )
                .first()
                .filesize  # type: ignore
            )
            for video in self.playlist.videos
        )
        return playlist_size

    def create_window(self) -> None:
        # -------------------- download window event loop
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

    def download(self, download_option: DownloadOption) -> None:
        if not self.folder:
            DOWNLOAD_DIR_POPUP()
            return

        download_dir: Path = self.rename_dir(
            self.folder,
            self.remove_forbidden_characters(self.playlist.title),
        )

        download_counter: int = 0
        for video in self.playlist.videos:
            (
                video.streams.filter(
                    resolution=download_option.RESOLUTION,
                    type=download_option.TYPE,
                    progressive=download_option.PROGRESSIVE,
                    abr=download_option.ABR,
                )
                .first()
                .download(  # type: ignore
                    output_path=download_dir,  # type: ignore
                    filename=f"{self.remove_forbidden_characters(video.title)}.mp4",
                )
            )
            download_counter += 1
            self.download_window["-DOWNLOADPROGRESS-"].update(download_counter)  # type: ignore
            self.download_window["-COMPLETED-"].update(
                f"{download_counter} of {self.playlist.length}"  # type: ignore
            )
        self.__download_complete()

    def __download_complete(self) -> None:
        """Helper method that resets the download progressbar and notifies the user when the download has finished."""
        self.download_window["-DOWNLOADPROGRESS-"].update(0)  # type: ignore
        self.download_window["-COMPLETED-"].update("")  # type: ignore
        sg.Popup("Download completed")


class VideoDownloader(YouTubeDownloader):
    """Class that contains and creates the window and necessary methods to download a YouTube video."""

    def __init__(self, url: str) -> None:
        """Initializes VideoDownloader instance.

        :param str url: YouTube video url
        """
        super().__init__(url)
        self.video: YouTube = YouTube(
            self.url,
            on_progress_callback=self.__progress_check,
            on_complete_callback=self.__on_complete,
        )

        # -------------------- defining layouts
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
                            sg.Text(HD.RESOLUTION),  # type: ignore
                            sg.Text(
                                f"{round(self.video.streams.get_by_resolution(HD.RESOLUTION).filesize / 1048576,1)} MB"  # type: ignore
                            ),
                        ]
                    ],
                )
            ],
            [
                sg.Frame(
                    "Lowest resolution",
                    [
                        [
                            sg.Button("Download", key="-LD-"),
                            sg.Text(LD.RESOLUTION),  # type: ignore
                            sg.Text(
                                f"{round(self.video.streams.get_by_resolution(LD.RESOLUTION).filesize / 1048576,1)} MB"  # type: ignore
                            ),
                        ]
                    ],
                )
            ],
            [
                sg.Frame(
                    "Audio only",
                    [
                        [
                            sg.Button("Download", key="-AUDIO-"),
                            sg.Text(
                                f"{round(self.video.streams.filter(type=AUDIO.TYPE, abr=AUDIO.ABR).first().filesize / 1048576,1)} MB"  # type: ignore
                            ),
                        ]
                    ],
                )
            ],
            [sg.VPush()],
            [
                sg.Text(
                    "",
                    key="-COMPLETED-",
                    size=(40, 1),
                    justification="c",
                    font="underline",
                )
            ],
            [
                sg.Progress(
                    100,
                    orientation="h",
                    size=(20, 20),
                    key="-DOWNLOADPROGRESS-",
                    expand_x=True,
                    bar_color="Black",
                )
            ],
        ]

        self.main_layout: list[list[sg.TabGroup]] = [
            [
                sg.TabGroup(
                    [[sg.Tab("info", info_tab), sg.Tab("download", download_tab)]]
                )
            ]
        ]

        self.download_window: sg.Window = sg.Window(
            "Youtube Downloader", self.main_layout, modal=True
        )

    def create_window(self) -> None:
        # -------------------- download window event loop
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

    def download(self, download_option: DownloadOption) -> None:
        if not self.folder:
            DOWNLOAD_DIR_POPUP()
            return
        (
            self.video.streams.filter(
                resolution=download_option.RESOLUTION,
                type=download_option.TYPE,
                progressive=download_option.PROGRESSIVE,
                abr=download_option.ABR,
            )
            .first()
            .download(  # type: ignore
                output_path=self.folder,  # type: ignore
                filename=f"{self.rename_file(self.folder, self.remove_forbidden_characters(self.video.title))}.mp4",
            )
        )

    def __progress_check(
        self, stream: Any, chunk: bytes, bytes_remaining: int
    ) -> None:  # parameters are necessary
        """Helper method that updated the progress bar when progress in the video download was made."""
        self.download_window["-DOWNLOADPROGRESS-"].update(
            100 - round(bytes_remaining / stream.filesize * 100)  # type: ignore
        )
        self.download_window["-COMPLETED-"].update(
            f"{100 - round(bytes_remaining / stream.filesize * 100)}% completed"  # type: ignore
        )

    def __on_complete(
        self, stream: Any, file_path: Optional[str]
    ) -> None:  # parameters are necessary
        """Helper method that resets the progress bar when the video download has finished."""
        self.download_window["-DOWNLOADPROGRESS-"].update(0)  # type: ignore
        self.download_window["-COMPLETED-"].update("")  # type: ignore
        sg.Popup("Download completed")
