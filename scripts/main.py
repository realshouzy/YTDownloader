#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import PySimpleGUI as sg
import re
from pytube.exceptions import RegexMatchError, VideoUnavailable, AgeRestrictedError, VideoPrivate, MembersOnly, VideoRegionBlocked
from windows import VideoDownloadWindow, PlaylistDownloadWindow


sg.theme('Darkred1')


def validate_url(url: str) -> PlaylistDownloadWindow|VideoDownloadWindow:
    """
    Helper function that validates wether the given url is a vaild YouTube Playlist or Video link.

    :param str url: YouTube url
    """
    db = {
        r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))\/playlist\?list=([0-9A-Za-z_-]{34})': PlaylistDownloadWindow,
        r'^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([0-9A-Za-z_-]{11})': VideoDownloadWindow
    }

    for k, v in db.items():
        if re.search(k, url):
            return v(url)
    raise RegexMatchError(validate_url, db)



def main() -> None:
    """
    Runs the program.
    """
    # -------------------- defining layouts
    start_layout = [
        [sg.Input(key='-LINKINPUT-'), sg.Button('Submit')],
    ]
    start_window = sg.Window('Youtube Downloader', start_layout)

    # -------------------- main event loop
    while True:
        try:
            event, values = start_window.read()
            if event == sg.WIN_CLOSED:
                break

            if event == 'Submit':
                download_window = validate_url(values['-LINKINPUT-'])
                if download_window is not None:
                    download_window.create()

        except RegexMatchError as rmx:
            if not values['-LINKINPUT-']:
                sg.Popup(f'Error: {type(rmx).__name__}', custom_text='Please provide link', title='Error')
            else:
                sg.Popup(f'Error: {type(rmx).__name__}', custom_text='Invalid link', title='Error')

        except AgeRestrictedError as arx:
            sg.Popup(f'Error: {type(arx).__name__}', custom_text='Video age restriced', title='Error')

        except VideoPrivate as vpx:
            sg.Popup(f'Error: {type(vpx).__name__}', custom_text='Video is privat', title='Error')

        except MembersOnly as mox:
            sg.Popup(f'Error: {type(mox).__name__}', custom_text='Video is for members only', title='Error')

        except VideoRegionBlocked as vgbx:
            sg.Popup(f'Error: {type(vgbx).__name__}', custom_text='Video is block in your region', title='Error')

        except VideoUnavailable as vux:
            sg.Popup(f'Error: {type(vux).__name__}', custom_text='Video Unavailable', title='Error')

        except Exception as x:
            sg.Popup(f'{type(x).__name__} at line {x.__traceback__.tb_lineno} of {__file__}: {x}', custom_text='Unexpected error', title='Error') 
            break

    start_window.close()




if __name__ == '__main__':
    main()