#!/usr/bin/env python3
"""
Setup script for MiniBiblio - Library Management System

This script packages the application for Windows deployment using cx_Freeze.
It creates a standalone executable that can run on Windows without requiring
a Python installation.
"""

import sys
import os
from pathlib import Path
from cx_Freeze import setup, Executable

# Application information
APP_NAME = "MiniBiblio"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Bibliotheksverwaltungssystem für kleine Bibliotheken"
APP_AUTHOR = "MiniBiblio Development Team"

# Build options for cx_Freeze
build_exe_options = {
    "packages": [
        "tkinter",
        "sqlite3",
        "datetime",
        "pathlib",
        "typing",
        "dataclasses",
        "tempfile",
        "unittest"
    ],
    "excludes": [
        "test",
        "unittest",
        "email",
        "html",
        "http",
        "urllib",
        "xml",
        "pydoc_data",
        "multiprocessing",
        "concurrent",
        "asyncio"
    ],
    "include_files": [
        # Include any additional files needed
        ("src/database/schema.sql", "lib/database/schema.sql"),
    ],
    "include_msvcrt": True,
    "optimize": 2,
    "zip_include_packages": ["*"],
    "zip_exclude_packages": [],
    "silent": True
}

# Base configuration for Windows GUI application
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Hide console window for GUI application

# Create executable configuration
executable = Executable(
    script="src/main.py",
    base=base,
    target_name="MiniBiblio.exe",
    icon=None,  # Add icon file path here if available
    copyright=f"Copyright (c) 2024 {APP_AUTHOR}",
    trademarks=""
)

# Setup configuration
setup(
    name=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    author=APP_AUTHOR,
    options={"build_exe": build_exe_options},
    executables=[executable]
)