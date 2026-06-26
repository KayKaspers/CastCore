"""Tests for the security-critical FFmpeg Command Builder."""

from __future__ import annotations

import pytest

from app.services.ffmpeg import (
    AudioSettings,
    CommandBuildError,
    FFmpegCommand,
    Input,
    Output,
    OutputFormat,
    VideoSettings,
    mask_command,
)


def test_basic_rtmp_reencode_argv_order():
    cmd = FFmpegCommand(
        inputs=[Input(uri="/data/media/clip.mp4", loop=True)],
        outputs=[
            Output(
                uri="rtmp://live.twitch.tv/app/STREAMKEY123",
                fmt=OutputFormat.FLV,
                video=VideoSettings(codec="libx264", bitrate="6000k", preset="veryfast", gop=50),
                audio=AudioSettings(codec="aac", bitrate="160k"),
            )
        ],
    )
    argv = cmd.build()
    assert argv[0] == "ffmpeg"
    # global options come first
    assert "-hide_banner" in argv
    # input (with loop) precedes output
    i_idx = argv.index("-i")
    assert argv[argv.index("-stream_loop")] == "-stream_loop" and argv.index("-stream_loop") < i_idx
    assert argv[i_idx + 1] == "/data/media/clip.mp4"
    # output codecs and format/uri at the end: "… -f flv <url>"
    assert "-c:v" in argv and "libx264" in argv
    assert argv[-3] == "-f" and argv[-2] == "flv"
    assert argv[-1] == "rtmp://live.twitch.tv/app/STREAMKEY123"


def test_stream_copy():
    cmd = FFmpegCommand(
        inputs=[Input(uri="udp://0.0.0.0:1234")],
        outputs=[Output(uri="rtmp://x/y/key", fmt=OutputFormat.FLV,
                        video=VideoSettings(codec="copy"), audio=AudioSettings(codec="copy"))],
    )
    argv = cmd.build()
    assert "-c:v" in argv and argv[argv.index("-c:v") + 1] == "copy"
    assert "-c:a" in argv and argv[argv.index("-c:a") + 1] == "copy"


def test_multiple_outputs():
    cmd = FFmpegCommand(
        inputs=[Input(uri="/data/media/a.mp4")],
        outputs=[
            Output(uri="rtmp://a/app/k1", fmt=OutputFormat.FLV, video=VideoSettings(codec="copy")),
            Output(uri="/data/recordings/out.mp4", fmt=OutputFormat.MP4, video=VideoSettings(codec="copy")),
        ],
    )
    argv = cmd.build()
    assert argv.count("-f") == 2
    assert "rtmp://a/app/k1" in argv
    assert "/data/recordings/out.mp4" in argv


def test_reconnect_options_for_network_input():
    cmd = FFmpegCommand(
        inputs=[Input(uri="https://example/stream.m3u8", reconnect=True)],
        outputs=[Output(uri="rtmp://x/y/k", fmt=OutputFormat.FLV, video=VideoSettings(codec="copy"))],
    )
    argv = cmd.build()
    assert "-reconnect" in argv and "-reconnect_delay_max" in argv


def test_requires_input_and_output():
    with pytest.raises(CommandBuildError) as e1:
        FFmpegCommand(inputs=[], outputs=[Output(uri="rtmp://x/y", fmt=OutputFormat.FLV)]).build()
    assert e1.value.code == "ffmpeg.no_input"

    with pytest.raises(CommandBuildError) as e2:
        FFmpegCommand(inputs=[Input(uri="/a.mp4")], outputs=[]).build()
    assert e2.value.code == "ffmpeg.no_output"


def test_rejects_unknown_codec():
    out = Output(uri="rtmp://x/y", fmt=OutputFormat.FLV, video=VideoSettings(codec="evil; rm -rf /"))
    with pytest.raises(CommandBuildError) as e:
        FFmpegCommand(inputs=[Input(uri="/a.mp4")], outputs=[out]).build()
    assert e.value.code == "ffmpeg.invalid_parameter"


def test_rejects_unsafe_uri_characters():
    # backticks / newlines must never reach argv even though there is no shell
    with pytest.raises(CommandBuildError):
        FFmpegCommand(
            inputs=[Input(uri="/a.mp4\n`whoami`")],
            outputs=[Output(uri="rtmp://x/y", fmt=OutputFormat.FLV, video=VideoSettings(codec="copy"))],
        ).build()


def test_preview_masks_rtmp_stream_key():
    cmd = FFmpegCommand(
        inputs=[Input(uri="/a.mp4")],
        outputs=[Output(uri="rtmp://live.twitch.tv/app/live_123456_SECRETKEY",
                        fmt=OutputFormat.FLV, video=VideoSettings(codec="copy"))],
    )
    preview = cmd.preview()
    assert "SECRETKEY" not in preview
    assert "••••" in preview


def test_mask_command_masks_query_secret():
    masked = mask_command(["ffmpeg", "-i", "srt://h:9000?streamid=x&password=topsecret"])
    assert "topsecret" not in masked
    assert "password=••••" in masked
