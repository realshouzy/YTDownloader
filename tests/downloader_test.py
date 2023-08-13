"""Tests for ``YTDownloader.downloader``."""
from __future__ import annotations

import inspect
from abc import ABC

import pytest

from YTDownloader.downloader import (
    _YOUTUBE_PLAYLIST_URL_PATTERN,
    _YOUTUBE_VIDEO_URL_PATTERN,
    PlaylistDownloader,
    VideoDownloader,
    YouTubeDownloader,
)

# pylint: disable=C0116, C0301

VALID_VIDEO_URLS: tuple[str, ...] = (
    "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "http://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=related",
    "http://youtu.be/dQw4w9WgXcQ",
    "http://www.youtube.com/embed/watch?feature=player_embedded&v=dQw4w9WgXcQ",
    "http://www.youtube.com/embed/watch?v=dQw4w9WgXcQ",
    "http://www.youtube.com/embed/v=dQw4w9WgXcQ",
    "http://www.youtube.com/watch?feature=player_embedded&v=dQw4w9WgXcQ",
    "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "www.youtube.com/watch?v=dQw4w9WgXcQ",
    "www.youtu.be/dQw4w9WgXcQ",
    "youtu.be/dQw4w9WgXcQ",
    "youtube.com/watch?v=dQw4w9WgXcQ",
    "http://www.youtube.com/watch/dQw4w9WgXcQ",
    "http://www.youtube.com/v/dQw4w9WgXcQ",
    "http://www.youtube.com/v/i_GFalTRHDA",
    "http://www.youtube.com/watch?v=i-GFalTRHDA&feature=related",
    "http://www.youtube.com/attribution_link?u=/watch?v=dQw4w9WgXcQ&feature=share&a=9QlmP1yvjcllp0h3l0NwuA",
    "http://www.youtube.com/attribution_link?a=dQw4w9WgXcQ&u=/watch?v=xvFZjo5PgG0&feature=em-uploademail",
    "http://www.youtube.com/attribution_link?a=dQw4w9WgXcQ&feature=em-uploademail&u=/watch?v=xvFZjo5PgG0",
)
VALID_PLAYLIST_URLS: tuple[str, ...] = (
    "https://www.youtube.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "https://youtube.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "www.youtube.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "youtube.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "https://www.youtube-nocookie.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "https://youtube-nocookie.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "www.youtube-nocookie.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "youtube-nocookie.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
)


@pytest.mark.parametrize("video_url", VALID_VIDEO_URLS)
def test_youtube_video_url_pattern_valid_urls(video_url: str) -> None:
    assert _YOUTUBE_VIDEO_URL_PATTERN.fullmatch(video_url) is not None


@pytest.mark.parametrize("playlist_url", VALID_PLAYLIST_URLS)
def test_youtube_playlist_url_pattern_valid_urls(playlist_url: str) -> None:
    assert _YOUTUBE_PLAYLIST_URL_PATTERN.fullmatch(playlist_url) is not None


def test_youtube_downloader_is_abc() -> None:
    assert inspect.isabstract(YouTubeDownloader)
    assert YouTubeDownloader.__base__ == ABC


def test_youtube_downloader_abstract_methods() -> None:
    # pylint: disable=E1101
    assert YouTubeDownloader.window.__isabstractmethod__
    assert YouTubeDownloader.download.__isabstractmethod__
    assert YouTubeDownloader.create_window.__isabstractmethod__


def test_video_downloader_inherits_from_youtube_downloader() -> None:
    assert VideoDownloader.__base__ == YouTubeDownloader

    # pylint: disable=E1101
    assert VideoDownloader.download.__override__
    assert VideoDownloader.create_window.__override__


def test_playlist_downloader_inherits_from_youtube_downloader() -> None:
    assert PlaylistDownloader.__base__ == YouTubeDownloader

    # pylint: disable=E1101
    assert PlaylistDownloader.download.__override__
    assert PlaylistDownloader.create_window.__override__
