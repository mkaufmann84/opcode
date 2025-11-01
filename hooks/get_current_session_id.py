#!/usr/bin/env python3
"""
Get current session ID by matching CWD
Usage: python3 get_current_session_id.py [cwd]
If no CWD provided, uses $PWD from environment
"""

import json
import sys
import os
from pathlib import Path

def get_current_session_id(cwd=None):
    """Find session ID by matching current working directory"""
    if cwd is None:
        cwd = os.environ.get("PWD", os.getcwd())

    # Normalize the CWD path
    cwd = str(Path(cwd).resolve())

    # Read the sessions file
    sessions_file = Path.home() / "local" / "global" / "claude-sessions.json"

    if not sessions_file.exists():
        print("ERROR: Sessions file not found", file=sys.stderr)
        return None

    with open(sessions_file, 'r') as f:
        data = json.load(f)

    sessions = data.get("sessions", [])

    # Find most recent session matching the CWD
    matching_sessions = [s for s in sessions if s.get("cwd") == cwd]

    if not matching_sessions:
        print(f"ERROR: No session found for CWD: {cwd}", file=sys.stderr)
        return None

    # Sort by last_activity (most recent first)
    matching_sessions.sort(key=lambda s: s.get("last_activity", 0), reverse=True)

    return matching_sessions[0]["session_id"]

if __name__ == "__main__":
    cwd = sys.argv[1] if len(sys.argv) > 1 else None
    session_id = get_current_session_id(cwd)

    if session_id:
        print(session_id)
        sys.exit(0)
    else:
        sys.exit(1)
