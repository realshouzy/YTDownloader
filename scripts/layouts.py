# -*- coding: UTF-8 -*-
import PySimpleGUI as sg

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