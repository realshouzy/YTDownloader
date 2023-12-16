"""Tests for ``YTDownloader.download_options``."""
from __future__ import annotations

from YTDownloader.download_options import AUDIO, HD, LD

# pylint: disable=C0116


def test_ld_options() -> None:
    assert LD.resolution == "360p"
    assert LD.type == "video"
    assert LD.progressive
    assert LD.abr is None


def test_hd_options() -> None:
    assert HD.resolution == "720p"
    assert HD.type == "video"
    assert HD.progressive
    assert HD.abr is None


def test_audio_options() -> None:
    assert AUDIO.resolution is None
    assert AUDIO.type == "audio"
    assert not AUDIO.progressive
    assert AUDIO.abr == "128kbps"
