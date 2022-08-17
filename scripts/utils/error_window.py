# -*- coding: UTF-8 -*-
"""Module containing the class to create a error window."""
from __future__ import annotations

import PySimpleGUI as sg
import webbrowser


class ErrorWindow:
    """
    Class that contains and creates an error window.
    """
    def __init__(self, error_name: Exception, error_message: str) -> None:
        self.ERROR: Exception = error_name
        self.ERROR_MESSAGE: str = error_message

        self.error_layout = [
            [sg.Text(f'{type(self.ERROR).__name__}: {self.ERROR_MESSAGE}')],
            [sg.Button('Ok', key='-OK-'), sg.Button('Report', key='-REPORT-')]
        ]

        self.error_window = sg.Window('Error', layout=self.error_layout, modal=True)

    def create(self) -> None:
        """
        Method that creates the event loop for the error window.
        """
        # -------------------- error window event loop
        while True:
            self.event, self.values = self.error_window.read()
            if self.event in {sg.WIN_CLOSED, '-OK-'}:
                break

            if self.event == '-REPORT-':
                webbrowser.open('https://github.com/realshouzy/YTDownloader/issues')

        self.error_window.close()