#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import PySimpleGUI as sg
from pytube.exceptions import RegexMatchError, VideoUnavailable
from windows import VideoDownloadWindow


sg.theme('Darkred1')


def main() -> None:
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
                download_window = VideoDownloadWindow(values['-LINKINPUT-'])
                download_window.create()                

        except RegexMatchError as rmx:
            if not values['-LINKINPUT-']:
                sg.Popup(f'Error: {type(rmx).__name__}', custom_text='Please provide link', title='Error')
            else:
                sg.Popup(f'Error: {type(rmx).__name__}', custom_text='Invalid link', title='Error')

        except VideoUnavailable as vux:
            sg.Popup(f'Error: {type(vux).__name__}', custom_text='Video Unavailable', title='Error')

        except Exception as x:
            sg.Popup(f'{type(x).__name__} at line {x.__traceback__.tb_lineno} of {__file__}: {x}', custom_text='Unexpected error', title='Error') 
            break

    start_window.close()




if __name__ == '__main__':
    main()