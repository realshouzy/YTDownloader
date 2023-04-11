#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module containing all a dataclass for the download option."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

__all__: list[str] = ["DownloadOption", "LD", "HD", "AUDIO"]


@dataclass(frozen=True, order=True, slots=True, kw_only=True)
class DownloadOption:
    """Class that defines and contains the download options."""

    resolution: Optional[str]
    type_: str
    progressive: bool
    abr: Optional[str]


# -------------------- defining download options
LD: DownloadOption = DownloadOption(
    resolution="360p",
    type_="video",
    progressive=True,
    abr=None,
)
HD: DownloadOption = DownloadOption(
    resolution="720p",
    type_="video",
    progressive=True,
    abr=None,
)
AUDIO: DownloadOption = DownloadOption(
    resolution=None,
    type_="audio",
    progressive=False,
    abr="128kbps",
)
