# ============================================================
# api/index.py — Vercel serverless entry point
#
# Vercel's Python runtime serves this module as a WSGI app.
# Our Flask `app` object is the WSGI callable.
# ============================================================

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402,F401
