# -*- coding: UTF-8 -*-
import PySimpleGUI as sg
import webbrowser
from pathlib import Path
from pytube import YouTube, Playlist
from typing import Any



class DownloadWindow:
    """
    Basic class that defines the most important constants, like the url or the download options (qualities).
    """
    def __init__(self, url: str) -> None:
        self.__URL = url
        self.DOWNLOAD_DIR_POPUP = lambda: sg.Popup('Please select a download directory', title='Info')
        
        # -------------------- defining download options
        self.LD = ('360p', 'video', True, None)
        self.HD = ('720p', 'video', True, None)
        self.AUDIO = (None, 'audio', False, '128kbps')

    @property
    def URL(self) -> str:
        return self.__URL

    def remove_forbidden_characters(self, text: str) -> str:
        """
        Helper method that removes '\\', '/', ':', '*', '?', '<', '>', '|' from a string.
    
        :param str text: string
        :return str: string with removed forbidden characters
        """
        forbidden_characters = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        for character in forbidden_characters:
            text = text.replace(character, '')
        return text



class PlaylistDownloadWindow(DownloadWindow):
    """
    Class that contains and creates the window and necessary methods to download a YouTube playlist.
    """
    def __init__(self, url: str) -> None:
        DownloadWindow.__init__(self, url)
        self.playlist_obj = Playlist(self.URL)

        # -------------------- defining layouts
        info_tab = [
            [sg.Text('URL:'), sg.Text(self.URL, enable_events=True, key='-URL-')],
            [sg.Text('Title:'), sg.Text(self.playlist_obj.title)],
            [sg.Text('Videos:'), sg.Text(self.playlist_obj.length)],
            [sg.Text('Views:'), sg.Text(self.playlist_obj.views)],
            [sg.Text('Owner:'), sg.Text(self.playlist_obj.owner, enable_events=True, key='-OWNER-')],
            [sg.Text('Last updated:'), sg.Text(self.playlist_obj.last_updated)]
        ]

        download_all_tab = [
            [sg.Text('Download Folder'), sg.Input(size=(53, 1), enable_events=True, key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Frame('Highest resolution', [[sg.Button('Download All', key='-HD-'), sg.Text(self.HD[0]), sg.Text(f'{self.calculate_size(self.HD)} MB')]])],
            [sg.Frame('Lowest resolution', [[sg.Button('Download All', key='-LD-'), sg.Text(self.LD[0]), sg.Text(f'{self.calculate_size(self.LD)} MB')]])],
            [sg.Frame('Audio only', [[sg.Button('Download All', key='-AUDIOALL-'), sg.Text(f'{self.calculate_size(self.AUDIO)} MB')]])],
            [sg.VPush()],
            [sg.Text('', key='-COMPLETED-', size=(57, 1), justification='c', font='underline')],
            [sg.Progress(self.playlist_obj.length, orientation='h', size=(20, 20), key='-DOWNLOADPROGRESS-', expand_x=True, bar_color='Black')]
        ]

        self.main_layout = [
            [sg.TabGroup([
                [sg.Tab('info', info_tab), sg.Tab('download all', download_all_tab)]
            ])]
        ]

        self.download_window: sg.Window = sg.Window('Youtube Downloader', self.main_layout, modal=True)
    

    def calculate_size(self, option: str) -> float:
        """
        Helper method that calculates the file size of a playlist, since pytube does not have this feature.

        :param str option: 
        """
        resolution, file_type, progressiv, abr = option
        playlist_size = 0
        for video_obj in self.playlist_obj.videos:
                playlist_size += video_obj.streams.filter(resolution=resolution, type=file_type, progressive=progressiv, abr=abr).first().filesize
            
        return round(playlist_size / 1048576, 1)

    
    def create(self) -> None:
        """
        Method that creates the event loop for the window.
        """
        # -------------------- download event loop
        while True:
            self.event, self.values = self.download_window.read()
            if self.event == sg.WIN_CLOSED:
                break
            
            if self.event == '-URL-':
                webbrowser.open(self.URL)

            if self.event == '-OWNER-':
                webbrowser.open(self.playlist_obj.owner_url)

            if self.event == '-HD-':
                self.download(self.HD)

            if self.event == '-LD-':
                self.download(self.LD)


            if self.event == '-AUDIOALL-':
                self.download(self.AUDIO)

        self.download_window.close()
            

    def download(self, option: Any) -> None:
        """
        Helper Method that downloads the the videos of the playlist.

        :param tuple option: tyuple containing the download options
        """
        if not self.values['-FOLDER-']:
            self.DOWNLOAD_DIR_POPUP()
            return
        
        resolution, file_type, progressiv, abr = option
        download_dir = self.rename_download_folder(self.values["-FOLDER-"], self.remove_forbidden_characters(self.playlist_obj.title))

        download_counter = 0
        for video_obj in self.playlist_obj.videos:
            video_obj.streams.filter(resolution=resolution, type=file_type, progressive=progressiv, abr=abr).first().download(output_path=download_dir, filename=f'{self.remove_forbidden_characters(video_obj.title)}.mp4')
            download_counter += 1
            self.download_window['-DOWNLOADPROGRESS-'].update(download_counter)
            self.download_window['-COMPLETED-'].update(f'{download_counter} of {self.playlist_obj.length}')
        self.download_complete()


    def download_complete(self) -> None:
        """
        Helper method that resets the download progressbar and notifies the user when the download has finished.
        """
        self.download_window['-DOWNLOADPROGRESS-'].update(0)
        self.download_window['-COMPLETED-'].update('')
        sg.Popup('Download completed')

    
    def rename_download_folder(self, root: Path, destination: Path) -> Path:
        """
        Helper method that renames the the folder if the user download the playlist more than once.

        :param Path root: Path in which the playlist folder will be created 
        :param Path destination: Folder in which the playlist will be downloaded

        :return Path original_path|new_path: Either the original path or if already downloaded renamed incremented path
        """
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



class VideoDownloadWindow(DownloadWindow):
    """
    Class that contains and creates the window and necessary methods to download a YouTube video.
    """
    def __init__(self, url: str) -> None:
        DownloadWindow.__init__(self, url)
        self.video_obj = YouTube(self.URL, on_progress_callback=self.__progress_check, on_complete_callback=self.__on_complete)

        # -------------------- defining layouts
        info_tab = [
            [sg.Text('URL:'), sg.Text(self.URL, enable_events=True, key='-URL-')],
            [sg.Text('Title:'), sg.Text(self.video_obj.title)],
            [sg.Text('Length:'), sg.Text(f'{round(self.video_obj.length / 60,2)} minutes')],
            [sg.Text('Views:'), sg.Text(self.video_obj.views)],
            [sg.Text('Creator:'), sg.Text(self.video_obj.author)],
            [sg.Text('Thumbnail:'), sg.Text(self.video_obj.thumbnail_url, enable_events=True, key='-THUMB-')],
            [sg.Text('Description:'), sg.Multiline(self.video_obj.description, size = (40, 20), no_scrollbar=True, disabled=True)]
        ]

        download_tab = [
            [sg.Text('Download Folder'), sg.Input(size=(27, 1), enable_events=True, key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Frame('Highest resolution', [[sg.Button('Download', key='-HD-'), sg.Text(self.HD[0]), sg.Text(f'{round(self.video_obj.streams.get_by_resolution(self.HD[0]).filesize / 1048576,1)} MB')]])],
            [sg.Frame('Lowest resolution', [[sg.Button('Download', key='-LD-'), sg.Text(self.LD[0]), sg.Text(f'{round(self.video_obj.streams.get_by_resolution(self.LD[0]).filesize / 1048576,1)} MB')]])],
            [sg.Frame('Audio only', [[sg.Button('Download', key='-AUDIO-'), sg.Text(f'{round(self.video_obj.streams.filter(type=self.AUDIO[1], abr=self.AUDIO[3]).first().filesize / 1048576,1)} MB')]])],
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


    def create(self) -> None:
        """
        Method that creates the event loop for the window.
        """
        # -------------------- download event loop
        while True:
            self.event, self.values = self.download_window.read()
            if self.event == sg.WIN_CLOSED:
                break

            if self.event == '-URL-':
                webbrowser.open(self.URL)
            
            if self.event == '-THUMB-':
                webbrowser.open(self.video_obj.thumbnail_url)
                
            if self.event == '-HD-':
                self.download_file(self.HD)

            if self.event == '-LD-':
                self.download_file(self.LD)
                
            if self.event == '-AUDIO-':
                self.download_file(self.AUDIO)
        self.download_window.close()


    def download_file(self, option: tuple[str|None, str, bool, str|None]) -> None:
        """
        Helper method that downloads the video in the given directory.

        :param tuple option: tyuple containing the download options
        """
        self.folder = self.values['-FOLDER-']
        resolution, file_type, progressiv, abr = option
        if not self.folder:
            self.DOWNLOAD_DIR_POPUP()
            return
        
        video = self.video_obj.streams.filter(resolution=resolution, type=file_type, progressive=progressiv, abr=abr).first()
        video.download(output_path=self.folder, filename=f'{self.rename_downloaded_file(self.video_obj.title)}.mp4')

    
    def rename_downloaded_file(self, file_name: str) -> str:
        """
        Helper method that renames the the file if the user download the video more than once.

        :param str file_name: video title
        :return str file_name|new_file_name: either original file name or new, incremented file name
        """
        file_name = self.remove_forbidden_characters(file_name)
        if Path(f'{self.folder}/{file_name}.mp4').exists():
            i = 1
            while True:
                i += 1
                new_file_name = f'{file_name} ({i})'

                if not Path(f'{self.folder}/{new_file_name}.mp4').exists():
                    return f'{new_file_name}'
        
        return f'{file_name}'


    def __progress_check(self, stream: Any, chunk: Any, bytes_remaining: Any) -> None:
        """
        Helper method that updated the progress bar when progress in the video download was made.
        Parameters are necessary.
        """
        self.download_window['-DOWNLOADPROGRESS-'].update(100 - round(bytes_remaining / stream.filesize * 100))
        self.download_window['-COMPLETED-'].update(f'{100 - round(bytes_remaining / stream.filesize * 100)}% completed')


    def __on_complete(self, stream: Any, file_path: Any) -> None:
        """
        Helper method that resets the progress bar when the video download has finished.
        Parameters are necessary.
        """
        self.download_window['-DOWNLOADPROGRESS-'].update(0)
        self.download_window['-COMPLETED-'].update('')
        sg.Popup('Download completed')
        


