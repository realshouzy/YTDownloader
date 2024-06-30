"""A program to download any YouTube video or playlist."""

from __future__ import annotations

__version__: Final[str] = "1.5.4"
__title__: Final[str] = "YTDownloader"
__author__: Final[str] = "realshouzy"
__license__: Final[str] = "MIT"
__copyright__: Final[str] = "Copyright (c) 2022-present realshouzy"

import re
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, NamedTuple, Protocol

import PySimpleGUI as sg
import pytube.exceptions
from pytube import Playlist, YouTube

if TYPE_CHECKING:
    from collections.abc import Iterator

    from pytube import Stream


class DownloadOptions(NamedTuple):
    """Tuple-like class holding the download options."""

    resolution: str | None
    type: str
    progressive: bool
    abr: str | None


# defining download options
LD: Final[DownloadOptions] = DownloadOptions(
    resolution="360p",
    type="video",
    progressive=True,
    abr=None,
)
HD: Final[DownloadOptions] = DownloadOptions(
    resolution="720p",
    type="video",
    progressive=True,
    abr=None,
)
AUDIO: Final[DownloadOptions] = DownloadOptions(
    resolution=None,
    type="audio",
    progressive=False,
    abr="128kbps",
)

_YOUTUBE_PLAYLIST_URL_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^(?:https?:\/\/)?(?:www\.|m\.)?"
    r"(?:youtube(?:-nocookie)?\.com|youtu.be)"
    r"\/playlist\?list=[\w\-_]{34}$",
)
_YOUTUBE_VIDEO_URL_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^(?:https?:\/\/)?(?:www\.|m\.)?"
    r"(?:youtube(?:-nocookie)?\.com|youtu.be)"
    r"\/?.*(?:watch|embed)?(?:.*v=|v\/|\/)[\w\-\_]{11}"
    r"(?:\S+)?(?:\?t=(?:\d+h)?(?:\d+m)?(?:\d+s)?(?:\d+))?$",
)


# defining helper functions
def _increment_playlist_dir_name(root: Path | str, sub: Path | str) -> Path:
    """Increment the directory if the user downloads a playlist more than once."""
    original_path: Path = Path(f"{root}/{sub}")
    if not original_path.exists():
        return original_path

    i: int = 1
    while Path(f"{root}/{sub} ({i})").exists():
        i += 1

    new_path: Path = Path(f"{root}/{sub} ({i})")
    return new_path


def _increment_video_file_name(root: Path | str, file_name: str) -> str:
    """Increment the file if the user downloads a video more than once."""
    file_path: Path = Path(f"{root}/{file_name}.mp4")
    if not file_path.exists():
        return file_name

    i: int = 1
    while Path(f"{root}/{file_name} ({i}).mp4").exists():
        i += 1

    new_file_name: str = f"{file_name} ({i})"
    return new_file_name


def _remove_forbidden_characters_from_file_name(name: str) -> str:
    r"""Remove '"' '\', '/', ':', '*', '?', '<', '>', '|' from a a file name.

    This avoids an OSError while saving or moving a file on Windows.
    """
    return "".join(char for char in name if char not in r'"\/:*?<>|')


def get_downloader(url: str) -> YouTubeDownloader:
    """Return the appropriate YouTube downloader based on the given url."""
    if _YOUTUBE_PLAYLIST_URL_PATTERN.fullmatch(url) is not None:
        return PlaylistDownloader(url)
    if _YOUTUBE_VIDEO_URL_PATTERN.fullmatch(url) is not None:
        return VideoDownloader(url)
    raise pytube.exceptions.RegexMatchError(
        get_downloader.__name__,
        f"({_YOUTUBE_PLAYLIST_URL_PATTERN.pattern}) | ({_YOUTUBE_VIDEO_URL_PATTERN.pattern})",
    )


def _get_stream_from_video(
    video: YouTube,
    download_options: DownloadOptions,
) -> Stream | None:
    """Return a stream filtered according to the download options."""
    return video.streams.filter(
        resolution=download_options.resolution,
        type=download_options.type,
        progressive=download_options.progressive,
        abr=download_options.abr,
    ).first()


def _download_dir_popup() -> None:  # pragma: no cover
    """Create an info pop telling 'Please select a download directory."""
    sg.Popup("Please select a download directory", title="Info")


def _resolution_unavailable_popup() -> None:  # pragma: no cover
    """Create an info pop telling 'This resolution is unavailable."""
    sg.Popup("This resolution is unavailable.", title="Info")


class YouTubeDownloader(Protocol):
    """GUI application for downloading YouTube content."""

    def create_window(self) -> None:
        """Create the event loop for the download window."""


class PlaylistDownloader:
    """Class handling the download of a YouTube playlist.

    It inherits from ``YouTubeDownloader``
    and implements playlist-specific download functionalities.
    """

    def __init__(self, url: str) -> None:
        self._url: str = url if url.startswith("https://") else f"https://{url}"
        self._playlist: Playlist = Playlist(self._url)

        # binding the playlists (list of streams) to corresponding download option
        hd_list: list[Stream | None] = self._get_playlist(HD)
        ld_list: list[Stream | None] = self._get_playlist(LD)
        audio_list: list[Stream | None] = self._get_playlist(AUDIO)
        self._stream_selection: dict[DownloadOptions, list[Stream] | None] = {
            HD: hd_list if None not in hd_list else None,
            LD: ld_list if None not in ld_list else None,
            AUDIO: audio_list if None not in audio_list else None,
        }

        # defining layouts
        info_tab: list[list[sg.Text]] = [
            [sg.Text("URL:"), sg.Text(self._url, enable_events=True, key="-URL-")],
            [sg.Text("Title:"), sg.Text(self._playlist.title)],
            [sg.Text("Videos:"), sg.Text(self._playlist.length)],
            [sg.Text("Views:"), sg.Text(f"{self._playlist.views:,}")],
            [
                sg.Text("Owner:"),
                sg.Text(self._playlist.owner, enable_events=True, key="-OWNER-"),
            ],
            [sg.Text("Last updated:"), sg.Text(self._playlist.last_updated)],
        ]

        download_all_tab: list[
            list[sg.Text | sg.Input | sg.Button]
            | list[sg.Frame]
            | list[sg.Text | sg.Input | sg.Frame]
            | list[sg.ProgressBar]
        ] = [
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
                            sg.Text(HD.resolution),
                            sg.Text(self._get_playlist_size(HD)),
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
                            sg.Text(LD.resolution),
                            sg.Text(self._get_playlist_size(LD)),
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
                            sg.Text(self._get_playlist_size(AUDIO)),
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
                sg.ProgressBar(
                    self._playlist.length,
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

        self._download_window: sg.Window = sg.Window(
            "Youtube Downloader",
            main_layout,
            modal=True,
        )

    def _get_playlist(
        self,
        download_options: DownloadOptions,
    ) -> list[Stream | None]:
        """Return a list of the streams to the corresponding download option by using threads."""
        with ThreadPoolExecutor() as executor:
            stream_list: list[Stream | None] = list(
                executor.map(
                    lambda stream: _get_stream_from_video(
                        stream,
                        download_options,
                    ),
                    self._playlist.videos,
                ),
            )
        return stream_list

    def _get_playlist_size(self, download_options: DownloadOptions) -> str:
        """Return the size of the playlist to the corresponding download option."""
        if (
            stream_selections := self._stream_selection[download_options]
        ) is None:  # pragma: no cover
            return "Unavailable"

        with ThreadPoolExecutor() as executor:
            stream_sizes: Iterator[int] = executor.map(
                lambda stream: stream.filesize,
                stream_selections,
            )
        return f"{round(sum(stream_sizes) / 1048576, 1)} MB"

    def create_window(self) -> None:  # pragma: no cover
        """Create the event loop for the download window."""
        # download window event loops
        while True:
            event, values = self._download_window.read()

            if event == sg.WIN_CLOSED:
                break

            if event == "-URL-":
                webbrowser.open(self._url)

            if event == "-OWNER-":
                webbrowser.open(self._playlist.owner_url)

            if event == "-HD-":
                self._download(HD, values["-FOLDER-"])

            if event == "-LD-":
                self._download(LD, values["-FOLDER-"])

            if event == "-AUDIOALL-":
                self._download(AUDIO, values["-FOLDER-"])

        self._download_window.close()

    def _download(
        self,
        download_options: DownloadOptions,
        download_dir: Path,
    ) -> None:  # pragma: no cover
        """Download the YouTube content into the given directory."""
        if not download_dir:
            _download_dir_popup()
            return

        if (streams_selection := self._stream_selection[download_options]) is None:
            _resolution_unavailable_popup()
            return

        download_path: Path = _increment_playlist_dir_name(
            download_dir,
            _remove_forbidden_characters_from_file_name(self._playlist.title),
        )

        for download_counter, video in enumerate(streams_selection, start=1):
            clean_filename: str = (
                f"{_remove_forbidden_characters_from_file_name(video.title)}.mp4"
            )
            video.download(output_path=str(download_path), filename=clean_filename)
            self._download_window["-DOWNLOADPROGRESS-"].update(download_counter)
            self._download_window["-COMPLETED-"].update(
                f"{download_counter} of {self._playlist.length}",
            )
        self._download_complete()

    def _download_complete(self) -> None:  # pragma: no cover
        """Reset the download progressbar and notifies the user when the download has finished."""
        self._download_window["-DOWNLOADPROGRESS-"].update(0)
        self._download_window["-COMPLETED-"].update("")
        sg.Popup("Download completed")


class VideoDownloader:
    """Class handling the download of a YouTube video.

    It inherits from ``YouTubeDownloader``
    and implements video-specific download functionalities.
    """

    def __init__(self, url: str) -> None:
        self._url: str = url if url.startswith("https://") else f"https://{url}"
        self._video: YouTube = YouTube(
            self._url,
            on_progress_callback=self._progress_check,
            on_complete_callback=self._download_complete,
        )

        # binding videos to corresponding download option
        self._stream_selection: dict[DownloadOptions, Stream | None] = {
            HD: _get_stream_from_video(self._video, HD),
            LD: _get_stream_from_video(self._video, LD),
            AUDIO: _get_stream_from_video(self._video, AUDIO),
        }

        # defining layouts
        info_tab: list[list[sg.Text | sg.Multiline]] = [
            [sg.Text("URL:"), sg.Text(self._url, enable_events=True, key="-URL-")],
            [sg.Text("Title:"), sg.Text(self._video.title)],
            [
                sg.Text("Length:"),
                sg.Text(f"{round(self._video.length / 60,2)} minutes"),
            ],
            [sg.Text("Views:"), sg.Text(f"{self._video.views:,}")],
            [
                sg.Text("Creator:"),
                sg.Text(self._video.author, enable_events=True, key="-CREATOR-"),
            ],
            [
                sg.Text("Thumbnail:"),
                sg.Text(self._video.thumbnail_url, enable_events=True, key="-THUMB-"),
            ],
            [
                sg.Text("Description:"),
                sg.Multiline(
                    self._video.description,
                    size=(40, 20),
                    no_scrollbar=True,
                    disabled=True,
                ),
            ],
        ]

        download_tab: list[
            list[sg.Text | sg.Input | sg.Button] | list[sg.Frame] | list[sg.ProgressBar]
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
                            sg.Text(HD.resolution),
                            sg.Text(self._get_video_size(HD)),
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
                            sg.Text(LD.resolution),
                            sg.Text(self._get_video_size(LD)),
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
                            sg.Text(self._get_video_size(AUDIO)),
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
                sg.ProgressBar(
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

        self._download_window: sg.Window = sg.Window(
            "Youtube Downloader",
            main_layout,
            modal=True,
        )

    def _get_video_size(self, download_options: DownloadOptions) -> str:
        """Return the size of the video to the corresponding download option."""
        if (stream_selection := self._stream_selection[download_options]) is None:
            return "Unavailable"
        return f"{round(stream_selection.filesize / 1048576, 1)} MB"

    def create_window(self) -> None:  # pragma: no cover
        """Create the event loop for the download window."""
        # download window event loop
        while True:
            event, values = self._download_window.read()

            if event == sg.WIN_CLOSED:
                break

            if event == "-URL-":
                webbrowser.open(self._url)

            if event == "-CREATOR-":
                webbrowser.open(self._video.channel_url)

            if event == "-THUMB-":
                webbrowser.open(self._video.thumbnail_url)

            if event == "-HD-":
                self._download(HD, values["-FOLDER-"])

            if event == "-LD-":
                self._download(LD, values["-FOLDER-"])

            if event == "-AUDIO-":
                self._download(AUDIO, values["-FOLDER-"])

        self._download_window.close()

    def _download(
        self,
        download_options: DownloadOptions,
        download_dir: Path,
    ) -> None:  # pragma: no cover
        """Download the YouTube content into the given directory."""
        if not download_dir:
            _download_dir_popup()
            return

        if (stream_selection := self._stream_selection[download_options]) is None:
            _resolution_unavailable_popup()
            return

        clean_video_title: str = _remove_forbidden_characters_from_file_name(
            self._video.title,
        )
        file_path: str = (
            f"{_increment_video_file_name(download_dir, clean_video_title)}.mp4"
        )

        stream_selection.download(output_path=str(download_dir), filename=file_path)

    # pylint: disable=W0613

    def _progress_check(
        self,
        stream: Any,
        chunk: bytes,
        bytes_remaining: int,
    ) -> None:  # pragma: no cover
        """Update the progress bar when progress in the download was made."""
        self._download_window["-DOWNLOADPROGRESS-"].update(
            100 - round(bytes_remaining / stream.filesize * 100),
        )
        self._download_window["-COMPLETED-"].update(r"100% completed")

    def _download_complete(
        self,
        stream: Any,
        file_path: str | None,
    ) -> None:  # pragma: no cover
        """Reset the progress bar when the video download has finished."""
        self._download_window["-DOWNLOADPROGRESS-"].update(0)
        self._download_window["-COMPLETED-"].update("")
        sg.Popup("Downloaded complete")


def create_error_window(error_name: str, message: str) -> None:  # pragma: no cover
    """Create an error window."""
    error_layout: list[list[sg.Text | sg.Button]] = [
        [sg.Text(f"{error_name}: {message}")],
        [sg.Button("Ok", key="-OK-"), sg.Button("Report", key="-REPORT-")],
    ]

    error_window: sg.Window = sg.Window(
        "Error",
        layout=error_layout,
        modal=True,
    )

    # error window event loop
    while True:
        event, _ = error_window.read()  # type: ignore
        if event in {sg.WIN_CLOSED, "-OK-"}:
            break
        if event == "-REPORT-":
            webbrowser.open("https://github.com/realshouzy/YTDownloader/issues")

    error_window.close()


# pylint: disable=R0912, W0718


def main() -> int:  # pragma: no cover
    """Run the program."""
    exit_code: int = 0

    sg.theme("Darkred1")

    # defining layouts
    start_layout: list[list[sg.Input | sg.Button]] = [
        [sg.Input(key="-LINKINPUT-"), sg.Button("Submit")],
    ]
    start_window: sg.Window = sg.Window("Youtube Downloader", start_layout)

    # main event loop
    while True:
        event, values = start_window.read()
        if event == sg.WIN_CLOSED:
            break

        if event == "Submit":
            try:
                downloader: YouTubeDownloader = get_downloader(
                    values["-LINKINPUT-"],
                )
                downloader.create_window()

            except pytube.exceptions.RegexMatchError as re_err:
                if not values["-LINKINPUT-"]:
                    create_error_window(
                        re_err.__class__.__name__,
                        "Please provide link.",
                    )
                else:
                    create_error_window(re_err.__class__.__name__, "Invalid link.")

            except pytube.exceptions.VideoUnavailable as vu_err:
                create_error_window(vu_err.__class__.__name__, vu_err.error_string)

            except pytube.exceptions.PytubeError as pytube_err:
                create_error_window(pytube_err.__class__.__name__, str(pytube_err))

            except KeyError as key_err:
                create_error_window(
                    key_err.__class__.__name__,
                    "Video or playlist is unreachable or invalid.",
                )

            except Exception as err:
                create_error_window(err.__class__.__name__, str(err))
                exit_code = 1
                break

    start_window.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
