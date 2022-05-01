# -*- coding: utf-8 -*-
import PySimpleGUI as sg
from pip import main
from pytube import YouTube
from pytube.exceptions import RegexMatchError
import webbrowser


def progress_check(stream, chunk, bytes_remaining):
    main_window['-DOWNLOADPROGRESS-'].update(100 - round(bytes_remaining / stream.filesize * 100))
    main_window['-COMPLETED-'].update(f'{100 - round(bytes_remaining / stream.filesize * 100)}% completed')

def on_complete(stream, file_path):
    main_window['-DOWNLOADPROGRESS-'].update(0)
    main_window['-COMPLETED-'].update('')
    sg.Popup('Download completed')

def download_dir_popup():
    sg.Popup('Please select a download directory', title='Info')

sg.theme('Darkred1')

# --------- defining layouts
start_layout = [
    [sg.Input(key='-LINKINPUT-'), sg.Button('Submit')],
]

info_tab = [
    [sg.Text('Link:'), sg.Text('', enable_events=True, key='-LINK-')],
    [sg.Text('Title:'), sg.Text('', key='-TITLE-')],
    [sg.Text('Length:'), sg.Text('', key='-LENGTH-')],
    [sg.Text('Views:'), sg.Text('', key='-VIEWS-')],
    [sg.Text('Creator:'), sg.Text('', key='-CREATOR-')],
    [sg.Text('Description:'), sg.Multiline('', key='-DESCRIPTION-', size = (40, 20), no_scrollbar=True, disabled=True)]
]

download_tab = [
    [sg.Text('Download Folder'), sg.Input(size=(27, 1), enable_events=True, key='-FOLDER-'), sg.FolderBrowse()],
    [sg.Frame('Best Quality', [[sg.Button('Download', key='-BEST-'), sg.Text('', key='-BESTRES-'), sg.Text('', key='-BESTSIZE-')]])],
    [sg.Frame('Worst Quality', [[sg.Button('Download', key='-WORST-'), sg.Text('', key='-WORSTRES-'), sg.Text('', key='-WORSTSIZE-')]])],
    [sg.Frame('Audio', [[sg.Button('Download', key='-AUDIO-'), sg.Text('', key='-AUDIOSIZE-')]])],
    [sg.VPush()],
    [sg.Text('', key='-COMPLETED-', size=(40, 1), justification='c', font='underline')],
    [sg.Progress(100, orientation='h', size=(20, 20), key='-DOWNLOADPROGRESS-', expand_x=True, bar_color='Black')]
]

main_layout = [
    [sg.TabGroup([
        [sg.Tab('info', info_tab), sg.Tab('download', download_tab)]
        ])
    ]
]


# --------- running programm
main_window = sg.Window('Youtube Downloader', start_layout)

# event loop
while True:
    try:
        event, values = main_window.read()
        if event == sg.WIN_CLOSED:
            break

        if event == 'Submit':
            link = values['-LINKINPUT-']
            video_object = YouTube(link, on_progress_callback=progress_check, on_complete_callback=on_complete)
            main_window.close()
                    
            # video info
            main_window  = sg.Window('Youtube Downloader', main_layout, finalize=True)
            main_window['-LINK-'].update(values['-LINKINPUT-'])
            main_window['-TITLE-'].update(video_object.title)
            main_window['-LENGTH-'].update(f'{round(video_object.length / 60,2)} minutes') 
            main_window['-VIEWS-'].update(video_object.views)
            main_window['-CREATOR-'].update(video_object.author)
            main_window['-DESCRIPTION-'].update(video_object.description)

            # download setup
            main_window['-BESTSIZE-'].update(f'{round(video_object.streams.get_highest_resolution().filesize / 1048576,1)} MB')
            main_window['-BESTRES-'].update(video_object.streams.get_highest_resolution().resolution)        

            main_window['-WORSTSIZE-'].update(f'{round(video_object.streams.get_lowest_resolution().filesize / 1048576,1)} MB')
            main_window['-WORSTRES-'].update(video_object.streams.get_lowest_resolution().resolution)

            main_window['-AUDIOSIZE-'].update(f'{round(video_object.streams.get_audio_only().filesize / 1048576,1)} MB')

        if event == '-LINK-':
            webbrowser.open(link)

        if event == '-BEST-':
            if not values['-FOLDER-']:
                download_dir_popup()
            else:
                video_object.streams.get_highest_resolution().download(values['-FOLDER-'])
            
        if event == '-WORST-':
            if not values['-FOLDER-']:
                download_dir_popup()
            else:
                video_object.streams.get_lowest_resolution().download(values['-FOLDER-'])
            
        if event == '-AUDIO-':
            if not values['-FOLDER-']:
                download_dir_popup()
            else:
                video_object.streams.get_audio_only().download(values['-FOLDER-'])

    except RegexMatchError as err:
        if not values['-LINKINPUT-']:
            sg.Popup(f'Error: {type(err).__name__}', custom_text='Please provide link', title='Error')
        else:
            sg.Popup(f'Error: {type(err).__name__}', custom_text='Invalid link', title='Error')

    except Exception as err:
        sg.Popup(f'{type(err).__name__} at line {err.__traceback__.tb_lineno} of {__file__}: {err}', custom_text='Unexpected error', title='Error') 
        break

main_window.close()