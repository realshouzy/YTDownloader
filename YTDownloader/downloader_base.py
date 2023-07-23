"""Module containing the base class for the YouTube downloader."""
from __future__ import annotations

__all__: list[str] = ["YouTubeDownloader"]

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

import PySimpleGUI as sg

if TYPE_CHECKING:
    from pytube import Stream, YouTube

    from YTDownloader.download_options import DownloadOptions


class YouTubeDownloader(ABC):
    """Abstract class that defines the most important needed (abstract) methods."""

    def __init__(self, url: str) -> None:
        self._url: str = url if url.startswith("https://") else f"https://{url}"

    @property
    def url(self) -> str:
        """The YouTube URL."""
        return self._url

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(url={self.url!r})"

    @staticmethod
    def _remove_forbidden_characters(name: str) -> str:
        r"""Remove '"' '\', '/', ':', '*', '?', '<', '>', '|' from a string.

        This avoids an OSError.
        """
        return "".join(char for char in name if char not in r'"\/:*?<>|')

    @staticmethod
    def _increment_dir_name(root: Path | str, sub: Path | str) -> Path:
        """Increment the directory if the user downloads a playlist more than once."""
        original_path: Path = Path(f"{root}/{sub}")
        if not original_path.exists():
            return original_path

        i: int = 1
        while Path(f"{root}/{sub} ({i})").exists():
            i += 1

        new_path: Path = Path(f"{root}/{sub} ({i})")
        return new_path

    @staticmethod
    def _increment_file_name(root: Path | str, file_name: str) -> str:
        """Increment the file if the user downloads a video more than once."""
        file_path: Path = Path(f"{root}/{file_name}.mp4")
        if not file_path.exists():
            return file_name

        i: int = 1
        while Path(f"{root}/{file_name} ({i}).mp4").exists():
            i += 1

        new_file_name: str = f"{file_name} ({i})"
        return new_file_name

    @staticmethod
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

    # defining popups
    @staticmethod
    def _download_dir_popup() -> None:
        """Create an info pop telling 'Please select a download directory.'."""
        sg.Popup("Please select a download directory", title="Info")

    @staticmethod
    def _resolution_unavailable_popup() -> None:
        """Create an info pop telling 'This resolution is unavailable.'."""
        sg.Popup("This resolution is unavailable.", title="Info")

    @abstractmethod
    def download(self, download_options: DownloadOptions) -> None:
        """Download the YouTube content into the given directory."""

    @abstractmethod
    def create_window(self) -> None:
        """Create the event loop for the download window."""
