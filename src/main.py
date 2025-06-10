#!/usr/bin/env python3
"""
MiniBiblio - Library Management System
Main application entry point
"""

import sys
import os
from pathlib import Path

# Ensure src directory is in Python path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import and run the main application
from ui.main_window import main

if __name__ == "__main__":
    main()