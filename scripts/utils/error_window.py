# -*- coding: UTF-8 -*-
"""Module containing the class to create a error window."""
from __future__ import annotations

import webbrowser
import PySimpleGUI as sg


class ErrorWindow:
    """
    Class that contains and creates an error window.
    """

    def __init__(self, error_name: Exception, error_message: str) -> None:
        self.error: Exception = error_name
        self.error_message: str = error_message

        self.error_layout: list[list[sg.Text | sg.Button]] = [
            [sg.Text(f"{self.error.__class__.__name__}: {self.error_message}")],
            [sg.Button("Ok", key="-OK-"), sg.Button("Report", key="-REPORT-")],
        ]

        self.error_window: sg.Window = sg.Window(
            "Error", layout=self.error_layout, modal=True
        )

    def create(self) -> None:
        """
        Method that creates the event loop for the error window.
        """
        # -------------------- error window event loop
        while True:
            event, _ = self.error_window.read()  # type: ignore
            if event in {sg.WIN_CLOSED, "-OK-"}:
                break
            if event == "-REPORT-":
                webbrowser.open("https://github.com/realshouzy/YTDownloader/issues")

        self.error_window.close()
