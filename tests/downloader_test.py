"""Tests for ``YTDownloader.downloader``."""
from __future__ import annotations

import inspect
from abc import ABC
from typing import TYPE_CHECKING

import pytest
import pytube.exceptions

from YTDownloader.downloader import (
    _YOUTUBE_PLAYLIST_URL_PATTERN,
    _YOUTUBE_VIDEO_URL_PATTERN,
    PlaylistDownloader,
    VideoDownloader,
    YouTubeDownloader,
    _increment_playlist_dir_name,
    _increment_video_file_name,
    _remove_forbidden_characters_from_file_name,
    get_downloader,
)

if TYPE_CHECKING:
    from pathlib import Path

# pylint: disable=C0116, C0301

VALID_VIDEO_URLS: list[str] = [
    "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=85s",
    "http://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=related",
    "http://youtu.be/dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ?t=85",
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
    "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
]

INVALID_VIDEO_URLS: list[str] = [
    "http://www.youtube.com",
    "http://www.youtube.com/watch?v=dQw4w9",
    "https://www.youtube.com/watch?v=",
    "http://www.youtube.com/watch?v=dQw4w9ture=related",
    "http://youtu.be/",
    "http://youtu.be/dQw4w9",
    "http://www.youtube.com/embed/watch?feature=player_embedded&v=dQw4w9",
    "http://www.youtube.com/embed/watch?v=dQw4w9",
    "http://www.youtube.com/embed/v=dQw4w9",
    "http://www.youtube.com/watch?feature=player_embedded&v=dQw4w9",
    "http://www.youtube.com/watch?v=dQw4w9",
    "www.youtube.com/watch?v=dQw4w9",
    "www.youtu.be/dQw4w9",
    "youtu.be/dQw4w9",
    "youtube.com/watch?v=dQw4w9",
    "http://www.youtube.com/watch",
    "http://www.youtube.com/watch/dQw4w9",
    "http://www.youtube.com/v",
    "http://www.youtube.com/v/dQw4w9",
]

VALID_PLAYLIST_URLS: list[str] = [
    "https://www.youtube.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "https://youtube.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "www.youtube.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "youtube.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "https://www.youtube-nocookie.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "https://youtube-nocookie.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "www.youtube-nocookie.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "youtube-nocookie.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
]

INVALID_PLAYLIST_URLS: list[str] = [
    "https://www.youtube.com/list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "https://www.youtube.com/playlist=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    "https://www.youtube.com/playlist?list=PL5--8gKSku15-C4m",
    "https://youtube.com/playlist?list=PL5--8gKSku15-C4m",
    "www.youtube.com/playlist?list=PL5--8gKSku15-C4m",
    "youtube.com/playlist?list=PL5--8gKSku15-C4m",
    "https://www.youtube-nocookie.com/playlist?list=PL5--8gKSku15-C4m",
    "https://youtube-nocookie.com/playlist?list=PL5--8gKSku15-C4m",
    "www.youtube-nocookie.com/playlist?list=PL5--8gKSku15-C4m",
    "youtube-nocookie.com/playlist?list=PL5--8gKSku15-C4m",
]


@pytest.mark.parametrize(
    "video_url",
    [
        *VALID_VIDEO_URLS,
        "https://www.youtube.com/watch?v=d_w4w9WgX-Q",
        "www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
        "https://youtube-nocookie.com/embed/dQw4w9WgXcQ",
        "youtube-nocookie.com/embed/dQw4w9WgXcQ",
        "http://www.youtube.com/watch?v=i-GFalTRHDA&feature=related",
        "http://www.youtube.com/attribution_link?u=/watch?v=dQw4w9WgXcQ&feature=share&a=9QlmP1yvjcllp0h3l0NwuA",
        "http://www.youtube.com/attribution_link?a=dQw4w9WgXcQ&u=/watch?v=xvFZjo5PgG0&feature=em-uploademail",
        "http://www.youtube.com/attribution_link?a=dQw4w9WgXcQ&feature=em-uploademail&u=/watch?v=xvFZjo5PgG0",
    ],
)
def test_youtube_video_url_pattern_valid_urls(video_url: str) -> None:
    assert _YOUTUBE_VIDEO_URL_PATTERN.fullmatch(video_url) is not None


@pytest.mark.parametrize("video_url", INVALID_VIDEO_URLS)
def test_invalid_video_url(video_url: str) -> None:
    assert _YOUTUBE_VIDEO_URL_PATTERN.fullmatch(video_url) is None


@pytest.mark.parametrize(
    "playlist_url",
    VALID_PLAYLIST_URLS,
)
def test_youtube_playlist_url_pattern_valid_urls(playlist_url: str) -> None:
    assert _YOUTUBE_PLAYLIST_URL_PATTERN.fullmatch(playlist_url) is not None


@pytest.mark.parametrize(
    "playlist_url",
    INVALID_PLAYLIST_URLS,
)
def test_invalid_playlist_url(playlist_url: str) -> None:
    assert _YOUTUBE_PLAYLIST_URL_PATTERN.fullmatch(playlist_url) is None


def test_increment_playlist_dir_name_not_exists(tmp_path: Path) -> None:
    root: Path = tmp_path
    sub = "playlist"

    result: Path = _increment_playlist_dir_name(root, sub)
    expected_path: Path = root / sub
    assert result == expected_path


def test_increment_playlist_dir_name_single_existing(tmp_path: Path) -> None:
    root: Path = tmp_path
    sub = "playlist"
    (root / sub).mkdir(parents=True, exist_ok=True)

    result: Path = _increment_playlist_dir_name(root, sub)
    expected_path: Path = root / f"{sub} (1)"
    assert result == expected_path


def test_increment_playlist_dir_name_multiple_existing(tmp_path: Path) -> None:
    root: Path = tmp_path
    sub = "playlist"
    (root / sub).mkdir(parents=True, exist_ok=True)
    for i in range(1, 3):
        (root / f"{sub} ({i})").mkdir(parents=True, exist_ok=True)

    result: Path = _increment_playlist_dir_name(root, sub)
    expected_path: Path = root / f"{sub} (3)"
    assert result == expected_path


def test_increment_video_file_name_not_exists(tmp_path: Path) -> None:
    root: Path = tmp_path
    file_name = "video"

    result: str = _increment_video_file_name(root, file_name)
    expected_file_name = "video"
    assert result == expected_file_name


def test_increment_video_file_name_single_existing(tmp_path: Path) -> None:
    root: Path = tmp_path
    file_name = "video"
    (root / f"{file_name}.mp4").touch()

    result: str = _increment_video_file_name(root, file_name)
    expected_file_name = "video (1)"
    assert result == expected_file_name


def test_increment_video_file_name_multiple_existing(tmp_path: Path) -> None:
    root: Path = tmp_path
    file_name = "video"
    (root / f"{file_name}.mp4").touch()
    for i in range(1, 4):
        (root / f"{file_name} ({i}).mp4").touch()

    result: str = _increment_video_file_name(root, file_name)
    expected_file_name = "video (4)"
    assert result == expected_file_name


@pytest.mark.parametrize(
    ("file_name", "expected_file_name"),
    [
        ("filename", "filename"),
        ('file"na/me:|', "filename"),
        (r'":/\*?<>|', ""),
        ("", ""),
    ],
)
def test_remove_forbidden_characters(file_name: str, expected_file_name: str) -> None:
    result: str = _remove_forbidden_characters_from_file_name(file_name)
    assert result == expected_file_name


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


@pytest.mark.parametrize(
    "video_url",
    VALID_VIDEO_URLS,
)
def test_get_downloader_for_video(video_url: str) -> None:
    downloader: PlaylistDownloader | VideoDownloader = get_downloader(video_url)
    assert isinstance(downloader, YouTubeDownloader)
    assert (
        downloader.url == video_url
        if video_url.startswith("https://")
        else f"https://{video_url}"
    )


@pytest.mark.parametrize(
    "playlist_url",
    VALID_PLAYLIST_URLS,
)
def test_get_downloader_for_playlist(playlist_url: str) -> None:
    downloader: PlaylistDownloader | VideoDownloader = get_downloader(playlist_url)
    assert isinstance(downloader, PlaylistDownloader)
    assert (
        downloader.url == playlist_url
        if playlist_url.startswith("https://")
        else f"https://{playlist_url}"
    )


@pytest.mark.parametrize(
    "invalid_url",
    [*INVALID_PLAYLIST_URLS, *INVALID_VIDEO_URLS],
)
def test_get_downloader_invalid_url_regex_error(invalid_url: str) -> None:
    with pytest.raises(pytube.exceptions.RegexMatchError):
        get_downloader(invalid_url)
