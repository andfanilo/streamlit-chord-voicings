import os

import requests
import streamlit.components.v1 as components

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


def st_visualize_chord():
    return _st_visualize_chord()
