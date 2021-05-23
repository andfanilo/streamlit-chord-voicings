import os
from typing import List

import requests
import streamlit.components.v1 as components
from music21.pitch import Pitch

_DEV_SERVER_URL = "http://localhost:1234"

try:
    r = requests.get(_DEV_SERVER_URL, timeout=2.50)
    assert r.status_code == 200
    _DEV_SERVER_UP = True
except requests.exceptions.ConnectionError:
    _DEV_SERVER_UP = False

if _DEV_SERVER_UP:
    _st_visualize_chord = components.declare_component(
        "chord_visualizer", url=_DEV_SERVER_URL,
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/dist")
    _st_visualize_chord = components.declare_component(
        "chord_visualizer", path=build_dir
    )


def st_visualize_chord(
    chord: List[Pitch] = ["c4", "g#4", "b4"],
    range_start: Pitch = Pitch("c3"),
    range_end: Pitch = Pitch("c6"),
    key: str = "key",
):
    _st_visualize_chord(
        notes=[n.midi for n in chord],
        rangeStart=range_start.nameWithOctave,
        rangeEnd=range_end.nameWithOctave,
        key=key,
    )
