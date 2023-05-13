#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Module containing all a dataclass for the download option."""
from __future__ import annotations

from typing import Final, NamedTuple, Optional

__all__: list[str] = ["DownloadOptions", "LD", "HD", "AUDIO"]


class DownloadOptions(NamedTuple):
    """Class that defines and contains the download options."""

    resolution: Optional[str]
    type: str  # noqa: A003
    progressive: bool
    abr: Optional[str]


# defining download options
LD: Final[DownloadOptions] = DownloadOptions(
    resolution="360p",
    type="video",
    progressive=True,
    abr=None,
)
HD: Final[DownloadOptions] = DownloadOptions(
    resolution="720p",
    type="video",
    progressive=True,
    abr=None,
)
AUDIO: Final[DownloadOptions] = DownloadOptions(
    resolution=None,
    type="audio",
    progressive=False,
    abr="128kbps",
)
