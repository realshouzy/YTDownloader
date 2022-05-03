#! /usr/bin/env python3
import PySimpleGUI as sg
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from layouts import start_layout, main_layout
import webbrowser


def progress_check(stream, chunk, bytes_remaining):
    main_window['-DOWNLOADPROGRESS-'].update(100 - round(bytes_remaining / stream.filesize * 100))
    main_window['-COMPLETED-'].update(f'{100 - round(bytes_remaining / stream.filesize * 100)}% completed')

def on_complete(stream, file_path):
    main_window['-DOWNLOADPROGRESS-'].update(0)
    main_window['-COMPLETED-'].update('')
    sg.Popup('Download completed')

download_dir_popup = lambda: sg.Popup('Please select a download directory', title='Info')


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
            main_window['-LINK-'].update(link)
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

    except RegexMatchError as rmx:
        if not values['-LINKINPUT-']:
            sg.Popup(f'Error: {type(rmx).__name__}', custom_text='Please provide link', title='Error')
        else:
            sg.Popup(f'Error: {type(rmx).__name__}', custom_text='Invalid link', title='Error')

    except Exception as x:
        sg.Popup(f'{type(x).__name__} at line {x.__traceback__.tb_lineno} of {__file__}: {x}', custom_text='Unexpected error', title='Error') 
        break

main_window.close()