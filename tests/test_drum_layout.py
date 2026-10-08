import os
import pytest
from airdrum.drum_layout import DrumLayout, DrumPad


def test_drum_pad_collision():
    pad = DrumPad(
        id="snare",
        name="Snare",
        x=0.2,
        y=0.2,
        width=0.4,
        height=0.4,
        color=(0, 255, 0),
        sound_file="snare.wav",
    )
    frame_w, frame_h = 1000, 1000

    # Test point inside bounding box (300, 300)
    assert pad.contains_point(300, 300, frame_w, frame_h) is True

    # Test point outside bounding box (100, 100)
    assert pad.contains_point(100, 100, frame_w, frame_h) is False


def test_drum_layout_loading(tmp_path):
    layout_file = tmp_path / "test_layout.json"
    layout_file.write_text(
        '{"pads": [{"id": "hihat", "name": "Hi-Hat", "x": 0.1, "y": 0.1, "width": 0.2, "height": 0.2, "color": [255, 0, 0]}]}'
    )

    layout = DrumLayout(str(layout_file))
    assert len(layout.pads) == 1
    assert layout.pads[0].id == "hihat"
    assert layout.pads[0].name == "Hi-Hat"