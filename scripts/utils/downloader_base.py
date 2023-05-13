#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module containing the base class for the YouTube downloader."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

import PySimpleGUI as sg

if TYPE_CHECKING:
    from .download_option import DownloadOptions

__all__: list[str] = ["YouTubeDownloader"]


class YouTubeDownloader(ABC):
    """Abstract class that defines the most important needed (abstract) methods."""

    def __init__(self, url: str) -> None:
        """Initializes Downloader instance.

        :param str url: YouTube url
        """
        self.url: str = url

    @staticmethod
    def remove_forbidden_characters(name: str) -> str:
        """Helper method that removes '"' '\', '/', ':', '*', '?', '<', '>', '|' from a string to avoid an OSError.

        :param str text: string
        :return str: string with removed forbidden characters
        """
        return "".join(char for char in name if char not in r'"\/:*?<>|')

    @staticmethod
    def increment_dir_name(root: Path | str, sub: Path | str) -> Path:
        """Helper method that renames the folder if the user download the playlist more than once.

        :param Path | str root: Path in which the playlist folder will be created
        :param Path | str sub: Folder in which the playlist will be downloaded

        :return Path original_path | new_path: Either the original path or if already downloaded renamed incremented path
        """
        original_path: Path = Path(f"{root}/{sub}")
        if not original_path.exists():
            return original_path

        i: int = 1
        while Path(f"{root}/{sub} ({i})").exists():
            i += 1

        new_path: Path = Path(f"{root}/{sub} ({i})")
        return new_path

    @staticmethod
    def increment_file_name(root: Path | str, file_name: str) -> str:
        """Helper method that renames the file if the user download the video more than once.

        :param Path | str root: Path in which the file will be downloaded
        :param str file_name: video title
        :return str file_name | new_file_name: either original file name or new, incremented file name
        """
        file_path: Path = Path(f"{root}/{file_name}.mp4")
        if not file_path.exists():
            return file_name

        i: int = 1
        while Path(f"{root}/{file_name} ({i}).mp4").exists():
            i += 1

        new_file_name: str = f"{file_name} ({i})"
        return new_file_name

    # defining popups
    @staticmethod
    def download_dir_popup() -> None:
        """Creates an info pop telling 'Please select a download directory.'"""
        sg.Popup("Please select a download directory", title="Info")

    @staticmethod
    def resolution_unavailable_popup() -> None:
        """Creates an info pop telling 'This resolution is unavailable.'"""
        sg.Popup("This resolution is unavailable.", title="Info")

    @abstractmethod
    def create_window(self) -> None:
        """Method that creates the event loop for the download window."""

    @abstractmethod
    def download(self, download_option: DownloadOptions) -> None:
        """Helper method that downloads the YouTube content into the given directory.

        :param tuple option: tuple containing the download options
        """
