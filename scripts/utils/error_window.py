#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module containing the class to create a error window."""
from __future__ import annotations

__all__: list[str] = ["create_error_window"]

import webbrowser

import PySimpleGUI as sg


def create_error_window(error_name: str, message: str) -> None:
    """Creates an error window."""
    error_layout: list[list[sg.Text | sg.Button]] = [
        [sg.Text(f"{error_name}: {message}")],
        [sg.Button("Ok", key="-OK-"), sg.Button("Report", key="-REPORT-")],
    ]

    error_window: sg.Window = sg.Window(
        "Error",
        layout=error_layout,
        modal=True,
    )

    # error window event loop
    while True:
        event, _ = error_window.read()  # type: ignore
        if event in {sg.WIN_CLOSED, "-OK-"}:
            break
        if event == "-REPORT-":
            webbrowser.open("https://github.com/realshouzy/YTDownloader/issues")

    error_window.close()
