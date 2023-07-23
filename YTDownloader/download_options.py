"""Module containing all a dataclass for the download option."""
from __future__ import annotations

__all__: list[str] = ["DownloadOptions", "LD", "HD", "AUDIO"]

from typing import Final, NamedTuple


class DownloadOptions(NamedTuple):
    """Tuple-like class that defines and contains the download options."""

    resolution: str | None
    type: str  # noqa: A003
    progressive: bool
    abr: str | None


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
