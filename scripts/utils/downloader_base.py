# -*- coding: UTF-8 -*-
"""Module containing the base class for the YouTube downloader."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .download_option import DownloadOption


class YouTubeDownloader(ABC):
    """Abstract class that defines the most important needed (abstract) methods."""

    def __init__(self, url: str) -> None:
        """Initializes Downloader instance.

        :param str url: YouTube url
        """
        self.url: str = url

    @staticmethod
    def remove_forbidden_characters(name: str) -> str:
        """Helper method that removes '\', '/', ':', '*', '?', '<', '>', '|' from a string to avoid an OSError.

        :param str text: string
        :return str: string with removed forbidden characters
        """
        return "".join(char for char in name if char not in r"\/:*?<>|")

    @staticmethod
    def rename_dir(root: Path | str, sub: Path | str) -> Path:
        """Helper method that renames the the folder if the user download the playlist more than once.

        :param Path | str root: Path in which the playlist folder will be created
        :param Path | str sub: Folder in which the playlist will be downloaded

        :return Path original_path | new_path: Either the original path or if already downloaded renamed incremented path
        """
        original_path: Path = Path(f"{root}/{sub}")
        if not original_path.exists():
            return original_path

        i: int = 1
        while True:
            i += 1
            new_path: Path = Path(f"{root}/{sub} ({i})")

            if not new_path.exists():
                return new_path

    @staticmethod
    def rename_file(root: Path | str, file_name: str) -> str:
        """Helper method that renames the the file if the user download the video more than once.

        :param Path | str root: Path in which the file will be downloaded
        :param str file_name: video title
        :return str file_name | new_file_name: either original file name or new, incremented file name
        """
        if not Path(f"{root}/{file_name}.mp4").exists():
            return file_name

        i: int = 1
        while True:
            i += 1
            new_file_name: str = f"{file_name} ({i})"

            if not Path(f"{root}/{new_file_name} ({i}).mp4").exists():
                return new_file_name

    @abstractmethod
    def create_window(self) -> None:
        """Method that creates the event loop for the download window."""

    @abstractmethod
    def download(self, download_option: DownloadOption) -> None:
        """Helper method that downloads the YouTube content into the given directory.

        :param tuple option: tuple containing the download options
        """
