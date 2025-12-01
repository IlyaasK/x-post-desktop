#!/bin/bash
cd "$(dirname "$0")"
GDK_BACKEND=wayland LD_PRELOAD=/usr/lib64/libgtk4-layer-shell.so.0 uv run main.py
