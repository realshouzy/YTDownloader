"""Tests for ``YTDownloader``."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import pytube.exceptions
from pytube import Playlist, Stream, YouTube

from YTDownloader import (
    _YOUTUBE_PLAYLIST_URL_PATTERN,
    _YOUTUBE_VIDEO_URL_PATTERN,
    AUDIO,
    HD,
    LD,
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

    from YTDownloader import DownloadOptions

# pylint: disable=C0116, C0301, W0621, W0212


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


VALID_VIDEO_URLS: list[str] = [
    "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=85s",
    "http://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=related",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=85s&feature=related",
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


@pytest.fixture(scope="session")
def youtube_video() -> YouTube:
    return YouTube("http://www.youtube.com/watch?v=dQw4w9WgXcQ")


@pytest.fixture(scope="session")
def youtube_playlist() -> Playlist:
    return Playlist(
        "https://www.youtube.com/playlist?list=PLJ_usHaf3fgOVAHKfe1SeVYYP8QRjqtSx",
    )


@pytest.fixture(scope="session")
def video_downloader(youtube_video: YouTube) -> VideoDownloader:
    return VideoDownloader(youtube_video.watch_url)


@pytest.fixture(scope="session")
def playlist_downloader(youtube_playlist: Playlist) -> PlaylistDownloader:
    return PlaylistDownloader(youtube_playlist.playlist_url)


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


# pylint: enable=E1101


def test_get_downloader_for_video() -> None:
    downloader: YouTubeDownloader = get_downloader(
        "www.youtube.com/watch?v=dQw4w9WgXcQ&t=85s&feature=related",
    )
    assert isinstance(downloader, VideoDownloader)
    assert (
        downloader._url
        == "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=85s&feature=related"
    )


def test_get_downloader_for_playlist() -> None:
    downloader: YouTubeDownloader = get_downloader(
        "www.youtube.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu",
    )
    assert isinstance(downloader, PlaylistDownloader)
    assert (
        downloader._url
        == "https://www.youtube.com/playlist?list=PL5--8gKSku15-C4mBKRpQVcaat4zwe4Gu"
    )


@pytest.mark.parametrize(
    "invalid_url",
    [
        *INVALID_VIDEO_URLS,
        *INVALID_PLAYLIST_URLS,
    ],
)
def test_get_downloader_invalid_url_regex_error(invalid_url: str) -> None:
    with pytest.raises(pytube.exceptions.RegexMatchError):
        get_downloader(invalid_url)


def test_video_property_video_downloader(
    youtube_video: YouTube,
    video_downloader: VideoDownloader,
) -> None:
    assert video_downloader._video == youtube_video


@pytest.mark.parametrize(
    ("download_options", "expected_size"),
    [
        pytest.param(HD, "19.3 MB", id="HD"),
        pytest.param(LD, "8.7 MB", id="LD"),
        pytest.param(AUDIO, "3.3 MB", id="AUDIO"),
    ],
)
def test_get_video_size_video_downloader(
    video_downloader: VideoDownloader,
    download_options: DownloadOptions,
    expected_size: str,
) -> None:
    assert video_downloader._get_video_size(download_options) == expected_size


@pytest.mark.parametrize(
    ("download_options", "expected_size"),
    [
        pytest.param(HD, "Unavailable", id="HD"),
        pytest.param(LD, "0.8 MB", id="LD"),
        pytest.param(AUDIO, "0.3 MB", id="AUDIO"),
    ],
)
def test_get_video_size_video_downloader_unavailable(
    download_options: DownloadOptions,
    expected_size: str,
) -> None:
    assert (
        VideoDownloader("https://www.youtube.com/watch?v=jNQXAC9IVRw")._get_video_size(
            download_options,
        )
        == expected_size
    )


@pytest.mark.parametrize(
    "download_options",
    [
        pytest.param(HD, id="HD"),
        pytest.param(LD, id="LD"),
        pytest.param(AUDIO, id="AUDIO"),
    ],
)
def test_stream_selection_video_downloader(
    video_downloader: VideoDownloader,
    download_options: DownloadOptions,
) -> None:
    stream_selection: Stream | None = video_downloader._stream_selection[
        download_options
    ]
    assert stream_selection is not None
    assert stream_selection.resolution == download_options.resolution
    assert stream_selection.type == download_options.type
    assert stream_selection.is_progressive is download_options.progressive

    if download_options.type == "audio":  # specific ABR is only relevant for audio
        assert stream_selection.abr == download_options.abr


def test_playlist_property_playlist_downloader(
    youtube_playlist: Playlist,
    playlist_downloader: PlaylistDownloader,
) -> None:
    assert playlist_downloader._playlist.videos == youtube_playlist.videos


@pytest.mark.parametrize(
    ("download_options", "expected_size"),
    [
        pytest.param(HD, "162.9 MB", id="HD"),
        pytest.param(LD, "104.2 MB", id="LD"),
        pytest.param(AUDIO, "71.2 MB", id="AUDIO"),
    ],
)
def test_get_playlist_size_playlist_downloader(
    playlist_downloader: PlaylistDownloader,
    download_options: DownloadOptions,
    expected_size: str,
) -> None:
    assert playlist_downloader._get_playlist_size(download_options) in {
        expected_size,
        "Unavailable",
    }


@pytest.mark.parametrize(
    "download_options",
    [
        pytest.param(HD, id="HD"),
        pytest.param(LD, id="LD"),
        pytest.param(AUDIO, id="AUDIO"),
    ],
)
def test_stream_selection_len_playlist_downloader(
    playlist_downloader: PlaylistDownloader,
    download_options: DownloadOptions,
) -> None:
    stream_selection: list[Stream] = playlist_downloader._stream_selection[  # type: ignore[assignment]
        download_options
    ]
    assert (
        stream_selection is None
        or len(stream_selection) == playlist_downloader._playlist.length
    )


@pytest.mark.parametrize(
    "download_options",
    [
        pytest.param(HD, id="HD"),
        pytest.param(LD, id="LD"),
        pytest.param(AUDIO, id="AUDIO"),
    ],
)
def test_stream_selection_playlist_downloader(
    playlist_downloader: PlaylistDownloader,
    download_options: DownloadOptions,
) -> None:
    stream_selection: list[Stream] = playlist_downloader._stream_selection[  # type: ignore[assignment]
        download_options
    ]

    if stream_selection is None:
        return

    for stream in stream_selection:
        assert stream.resolution == download_options.resolution
        assert stream.type == download_options.type
        assert stream.is_progressive is download_options.progressive

        if download_options.type == "audio":  # specific ABR is only relevant for audio
            assert stream.abr == download_options.abr
            assert stream.abr == download_options.abr
