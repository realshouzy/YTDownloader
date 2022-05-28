# -*- coding: UTF-8 -*-
import PySimpleGUI as sg
from pytube import YouTube
import webbrowser
from typing import Any


class VideoDownloadWindow:
    def __init__(self, link: str) -> None:
        self.__link: str = link
        self.video_obj: YouTube = YouTube(self.link, on_progress_callback=self.__progress_check, on_complete_callback=self.__on_complete)

        # -------------------- defining layouts
        info_tab = [
            [sg.Text('Link:'), sg.Text(self.link, enable_events=True, key='-LINK-')],
            [sg.Text('Title:'), sg.Text(self.video_obj.title)],
            [sg.Text('Length:'), sg.Text(f'{round(self.video_obj.length / 60,2)} minutes')],
            [sg.Text('Views:'), sg.Text(self.video_obj.views)],
            [sg.Text('Creator:'), sg.Text(self.video_obj.author)],
            [sg.Text('Description:'), sg.Multiline(self.video_obj.description, size = (40, 20), no_scrollbar=True, disabled=True)]
        ]

        download_tab = [
            [sg.Text('Download Folder'), sg.Input(size=(27, 1), enable_events=True, key='-FOLDER-'), sg.FolderBrowse()],
            [sg.Frame('Best Quality', [[sg.Button('Download', key='-BEST-'), sg.Text(self.video_obj.streams.get_highest_resolution().resolution), sg.Text(f'{round(self.video_obj.streams.get_highest_resolution().filesize / 1048576,1)} MB')]])],
            [sg.Frame('Worst Quality', [[sg.Button('Download', key='-WORST-'), sg.Text(self.video_obj.streams.get_lowest_resolution().resolution), sg.Text(f'{round(self.video_obj.streams.get_lowest_resolution().filesize / 1048576,1)} MB')]])],
            [sg.Frame('Audio', [[sg.Button('Download', key='-AUDIO-'), sg.Text(f'{round(self.video_obj.streams.get_audio_only().filesize / 1048576,1)} MB')]])],
            [sg.VPush()],
            [sg.Text('', key='-COMPLETED-', size=(40, 1), justification='c', font='underline')],
            [sg.Progress(100, orientation='h', size=(20, 20), key='-DOWNLOADPROGRESS-', expand_x=True, bar_color='Black')]
        ]

        self.main_layout = [
            [sg.TabGroup([
                [sg.Tab('info', info_tab), sg.Tab('download', download_tab)]
                ])
            ]
        ]
        
        # -------------------- defining windows and popups
        self.download_window: sg.Window = sg.Window('Youtube Downloader', self.main_layout, modal=True)
        self.download_dir_popup = lambda: sg.Popup('Please select a download directory', title='Info')


    def create(self) -> None:
        # -------------------- download event loop
        while True:
            self.event, self.values = self.download_window.read()
            if self.event == sg.WIN_CLOSED:
                break

            if self.event == '-LINK-':
                webbrowser.open(self.link)

            if self.event == '-BEST-':
                self.download(self.video_obj.streams.get_highest_resolution().download)
                
            if self.event == '-WORST-':
                self.download(self.video_obj.streams.get_lowest_resolution().download)
                
            if self.event == '-AUDIO-':
                self.download(self.video_obj.streams.get_audio_only().download)
        self.download_window.close()


    def download(self, option: Any) -> None:
        if not self.values['-FOLDER-']:
            self.download_dir_popup()
        else:
            option(self.values['-FOLDER-'])

    @property
    def link(self) -> str:
        return self.__link


    def __progress_check(self, stream: Any, chunk: Any, bytes_remaining: Any) -> None:
        self.download_window['-DOWNLOADPROGRESS-'].update(100 - round(bytes_remaining / stream.filesize * 100))
        self.download_window['-COMPLETED-'].update(f'{100 - round(bytes_remaining / stream.filesize * 100)}% completed')


    def __on_complete(self, stream: Any, file_path: Any) -> None:
        self.download_window['-DOWNLOADPROGRESS-'].update(0)
        self.download_window['-COMPLETED-'].update('')
        sg.Popup('Download completed')
        


