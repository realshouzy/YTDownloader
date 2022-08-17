# -*- coding: UTF-8 -*-
"""
Module containing all classes to download YouTube content.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, overload

import PySimpleGUI as sg
from pytube import YouTube, Playlist
import webbrowser

from dataclasses import dataclass, field
from abc import ABC, abstractmethod


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


    def remove_forbidden_characters(self, text: str) -> str:
        """
        Helper method that removes '\', '/', ':', '*', '?', '<', '>', '|' from a string to avoid a OSError.
    
        :param str text: string
        :return str: string with removed forbidden characters
        """
        forbidden_characters = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        for character in forbidden_characters:
            new_text = text.replace(character, '')
        return new_text

  
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

    
    @abstractmethod
    @overload
    def rename_download(self, root: Path, destination: Path) -> Path:
        """
        Helper method that renames the the folder if the user download the playlist more than once.

        :param Path root: Path in which the playlist folder will be created 
        :param Path destination: Folder in which the playlist will be downloaded

        :return Path original_path | new_path: Either the original path or if already downloaded renamed incremented path
        """

    
    @abstractmethod
    @overload
    def rename_download(self, file_name: str) -> str:
        """
        Helper method that renames the the file if the user download the video more than once.

        :param str file_name: video title
        :return str file_name | new_file_name: either original file name or new, incremented file name
        """


class PlaylistDownloader(YouTubeDownloader):
    """
    Class that contains and creates the window and necessary methods to download a YouTube playlist.
    """
    def __init__(self, url: str) -> None:
        """
        Initializes PlaylistDownloader instance.

        :param str url: YouTube playlist url
        """
        YouTubeDownloader.__init__(self, url)
        self.playlist = Playlist(self.URL)

        # -------------------- defining layouts
        info_tab = [
            [sg.Text('URL:'), sg.Text(self.URL, enable_events=True, key='-URL-')],
            [sg.Text('Title:'), sg.Text(self.playlist.title)],
            [sg.Text('Videos:'), sg.Text(self.playlist.length)],
            [sg.Text('Views:'), sg.Text(f'{self.playlist.views:,}')],
            [sg.Text('Owner:'), sg.Text(self.playlist.owner, enable_events=True, key='-OWNER-')],
            [sg.Text('Last updated:'), sg.Text(self.playlist.last_updated)]
        ]

        download_all_tab = [
            [sg.Text('Download Folder'), sg.Input(size=(53, 1), enable_events=True, key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Frame('Highest resolution', [[sg.Button('Download All', key='-HD-'), sg.Text(self.HD.RESOLUTION), sg.Text(f'{self.calculate_playlist_size(self.HD)} MB')]])],
            [sg.Frame('Lowest resolution', [[sg.Button('Download All', key='-LD-'), sg.Text(self.LD.RESOLUTION), sg.Text(f'{self.calculate_playlist_size(self.LD)} MB')]])],
            [sg.Frame('Audio only', [[sg.Button('Download All', key='-AUDIOALL-'), sg.Text(f'{self.calculate_playlist_size(self.AUDIO)} MB')]])],
            [sg.VPush()],
            [sg.Text('', key='-COMPLETED-', size=(57, 1), justification='c', font='underline')],
            [sg.Progress(self.playlist.length, orientation='h', size=(20, 20), key='-DOWNLOADPROGRESS-', expand_x=True, bar_color='Black')]
        ]

        self.main_layout = [
            [sg.TabGroup([
                [sg.Tab('info', info_tab), sg.Tab('download all', download_all_tab)]
            ])]
        ]

        self.download_window: sg.Window = sg.Window('Youtube Downloader', self.main_layout, modal=True)
    

    def calculate_playlist_size(self, download_option: DownloadOption) -> float:
        """
        Helper method that calculates the file size of a playlist, since pytube does not have this feature.

        :param DownloadOption option: class containing the download options
        :return float: size of the playlist
        """
        playlist_size = 0
        for video in self.playlist.videos:
                playlist_size += (
                    video.streams.filter(resolution=download_option.RESOLUTION, type=download_option.TYPE, progressive=download_option.PROGRESSIVE, abr=download_option.ABR)
                     .first().filesize
                )
        return round(playlist_size / 1048576, 1)

    
    def create_window(self) -> None:
        # -------------------- download window event loop
        while True:
            self.event, self.values = self.download_window.read()
            if self.event == sg.WIN_CLOSED:
                break
            
            if self.event == '-URL-':
                webbrowser.open(self.URL)

            if self.event == '-OWNER-':
                webbrowser.open(self.playlist.owner_url)

            if self.event == '-HD-':
                self.download(self.HD)

            if self.event == '-LD-':
                self.download(self.LD)

            if self.event == '-AUDIOALL-':
                self.download(self.AUDIO)

        self.download_window.close()
            

    def download(self, download_option: DownloadOption) -> None:
        if not self.values['-FOLDER-']:
            self.DOWNLOAD_DIR_POPUP()
            return

        download_dir = self.rename_download(Path(self.values["-FOLDER-"]), Path(self.remove_forbidden_characters(self.playlist.title)))

        download_counter = 0
        for video in self.playlist.videos:
            (
             video.streams.filter(resolution=download_option.RESOLUTION, type=download_option.TYPE, progressive=download_option.PROGRESSIVE, abr=download_option.ABR)
                .first()
                .download(output_path=download_dir, filename=f'{self.remove_forbidden_characters(video.title)}.mp4')
            )
            download_counter += 1
            self.download_window['-DOWNLOADPROGRESS-'].update(download_counter)
            self.download_window['-COMPLETED-'].update(f'{download_counter} of {self.playlist.length}')
        self._download_complete()


    def _download_complete(self) -> None:
        """
        Helper method that resets the download progressbar and notifies the user when the download has finished.
        """
        self.download_window['-DOWNLOADPROGRESS-'].update(0)
        self.download_window['-COMPLETED-'].update('')
        sg.Popup('Download completed')

    
    def rename_download(self, root: Path, destination: Path) -> Path:
        original_path = Path(f'{root}/{destination}')
        if original_path.exists():
            i = 1
            while True:
                i += 1
                new_destination = Path(f'{destination} ({i})')
                new_path = Path(f'{root}/{new_destination}')

                if not new_path.exists():
                    return new_path

        return original_path



class VideoDownloader(YouTubeDownloader):
    """
    Class that contains and creates the window and necessary methods to download a YouTube video.
    """
    def __init__(self, url: str) -> None:
        """
        Initializes VideoDownloader instance.

        :param str url: YouTube video url
        """
        YouTubeDownloader.__init__(self, url)
        self.video = YouTube(self.URL, on_progress_callback=self.__progress_check, on_complete_callback=self.__on_complete)

        # -------------------- defining layouts
        info_tab = [
            [sg.Text('URL:'), sg.Text(self.URL, enable_events=True, key='-URL-')],
            [sg.Text('Title:'), sg.Text(self.video.title)],
            [sg.Text('Length:'), sg.Text(f'{round(self.video.length / 60,2)} minutes')],
            [sg.Text('Views:'), sg.Text(f'{self.video.views:,}')],
            [sg.Text('Creator:'), sg.Text(self.video.author, enable_events=True, key='-CREATOR-')],
            [sg.Text('Thumbnail:'), sg.Text(self.video.thumbnail_url, enable_events=True, key='-THUMB-')],
            [sg.Text('Description:'), sg.Multiline(self.video.description, size = (40, 20), no_scrollbar=True, disabled=True)]
        ]

        download_tab = [
            [sg.Text('Download Folder'), sg.Input(size=(27, 1), enable_events=True, key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Frame('Highest resolution', [[sg.Button('Download', key='-HD-'), sg.Text(self.HD.RESOLUTION), sg.Text(f'{round(self.video.streams.get_by_resolution(self.HD.RESOLUTION).filesize / 1048576,1)} MB')]])],
            [sg.Frame('Lowest resolution', [[sg.Button('Download', key='-LD-'), sg.Text(self.LD.RESOLUTION), sg.Text(f'{round(self.video.streams.get_by_resolution(self.LD.RESOLUTION).filesize / 1048576,1)} MB')]])],
            [sg.Frame('Audio only', [[sg.Button('Download', key='-AUDIO-'), sg.Text(f'{round(self.video.streams.filter(type=self.AUDIO.TYPE, abr=self.AUDIO.ABR).first().filesize / 1048576,1)} MB')]])],
            [sg.VPush()],
            [sg.Text('', key='-COMPLETED-', size=(40, 1), justification='c', font='underline')],
            [sg.Progress(100, orientation='h', size=(20, 20), key='-DOWNLOADPROGRESS-', expand_x=True, bar_color='Black')]
        ]

        self.main_layout = [
            [sg.TabGroup([
                [sg.Tab('info', info_tab), sg.Tab('download', download_tab)]
                ])]
        ]

        self.download_window: sg.Window = sg.Window('Youtube Downloader', self.main_layout, modal=True)


    def create_window(self) -> None:
        # -------------------- download window event loop
        while True:
            self.event, self.values = self.download_window.read()
            if self.event == sg.WIN_CLOSED:
                break

            if self.event == '-URL-':
                webbrowser.open(self.URL)

            if self.event == '-CREATOR-':
                webbrowser.open(self.video.channel_url)
            
            if self.event == '-THUMB-':
                webbrowser.open(self.video.thumbnail_url)
                
            if self.event == '-HD-':
                self.download(self.HD)

            if self.event == '-LD-':
                self.download(self.LD)
                
            if self.event == '-AUDIO-':
                self.download(self.AUDIO)
                
        self.download_window.close()


    def download(self, download_option: DownloadOption) -> None:
        self.folder = self.values['-FOLDER-']
        if not self.folder:
            self.DOWNLOAD_DIR_POPUP()
            return
        (
         self.video.streams.filter(resolution=download_option.RESOLUTION, type=download_option.TYPE, progressive=download_option.PROGRESSIVE, abr=download_option.ABR)
            .first()
            .download(output_path=self.folder, filename=f'{self.rename_downloaded(self.video.title)}.mp4')
        )
    
    def rename_downloaded(self, file_name: str) -> str:
        file_name = self.remove_forbidden_characters(file_name)
        if Path(f'{self.folder}/{file_name}.mp4').exists():
            i = 1
            while True:
                i += 1
                new_file_name = f'{file_name} ({i})'

                if not Path(f'{self.folder}/{new_file_name}.mp4').exists():
                    return f'{new_file_name}'
        
        return f'{file_name}'


    def __progress_check(self, stream: Any, chunk: bytes, bytes_remaining: int) -> None:
        """
        Helper method that updated the progress bar when progress in the video download was made.
        Parameters are necessary.
        """
        self.download_window['-DOWNLOADPROGRESS-'].update(100 - round(bytes_remaining / stream.filesize * 100))
        self.download_window['-COMPLETED-'].update(f'{100 - round(bytes_remaining / stream.filesize * 100)}% completed')


    def __on_complete(self, stream: Any, file_path: str | None) -> None:
        """
        Helper method that resets the progress bar when the video download has finished.
        Parameters are necessary.
        """
        self.download_window['-DOWNLOADPROGRESS-'].update(0)
        self.download_window['-COMPLETED-'].update('')
        sg.Popup('Download completed')