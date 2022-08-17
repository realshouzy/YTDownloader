# -*- coding: UTF-8 -*-
from __future__ import annotations
from pathlib import Path
from typing import overload

import PySimpleGUI as sg
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True, order=True)
class DownloadOption:
    """
    Class that defines and contains the download options and represents them as a tuple.
    """
    RESOLUTION: str | None
    TYPE: str
    PROGRESSIVE: bool
    ABR: str | None



@dataclass(frozen=True)
class YouTubeDownloader(ABC):
    """
    Abstract class that defines the most important constants, like the url and contains the download options (qualities) as well as defines needed (abstract) methods.
    """
    URL: str
    DOWNLOAD_DIR_POPUP: sg.Popup = field(default=lambda self: sg.Popup('Please select a download directory', title='Info'), init=False)

    # -------------------- defining download options
    LD: DownloadOption = field(default=DownloadOption('360p', 'video', True, None), init=False)
    HD: DownloadOption = field(default=DownloadOption('720p', 'video', True, None), init=False)
    AUDIO: DownloadOption = field(default=DownloadOption(None, 'audio', False, '128kbps'), init=False)


    def remove_forbidden_characters(self, file_name: str) -> str:
        """
        Helper method that removes '\', '/', ':', '*', '?', '<', '>', '|' from a string to avoid a OSError.
    
        :param str text: string
        :return str: string with removed forbidden characters
        """
        forbidden_characters = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        for character in forbidden_characters:
            new_file_name = file_name.replace(character, '')
        return new_file_name

  
    @abstractmethod
    def create_window(self) -> None:
        """
        Method that creates the event loop for the download window.
        """


    @abstractmethod
    def download(self, download_option: DownloadOption) -> None:
        """
        Helper method that downloads the YouTube content into the given directory.

        :param tuple option: tuple containing the download options
        """


    @overload
    @abstractmethod
    def rename_download(self, root: Path, destination: Path) -> Path:
        """
        Helper method that renames the the folder if the user download the playlist more than once.

        :param Path root: Path in which the playlist folder will be created 
        :param Path destination: Folder in which the playlist will be downloaded

        :return Path original_path | new_path: Either the original path or if already downloaded renamed incremented path
        """


    @overload
    @abstractmethod
    def rename_download(self, file_name: str) -> str:
        """
        Helper method that renames the the file if the user download the video more than once.

        :param str file_name: video title
        :return str file_name | new_file_name: either original file name or new, incremented file name
        """