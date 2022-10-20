# -*- coding: UTF-8 -*-
"""
Module containing all a dataclass for the download option.
"""
from __future__ import annotations
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True, order=True, slots=True)
class DownloadOption:
    """
    Class that defines and contains the download options.
    """

    RESOLUTION: Optional[str]
    TYPE: str
    PROGRESSIVE: bool
    ABR: Optional[str]
