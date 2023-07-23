"""Module containing the base class for the YouTube downloader."""
from __future__ import annotations

__all__: list[str] = ["YouTubeDownloader"]

from abc import ABC, abstractmethod
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
