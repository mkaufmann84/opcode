#!/usr/bin/env python3
"""
SessionStart Hook
Registers a new Claude Code session when it starts
"""

import json
import sys
import time
from pathlib import Path

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent))
import hook_utils
import session_settings

def main():
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        session_id = input_data.get("session_id")
        if not session_id:
            # No session ID available yet, skip
            sys.exit(0)

        # Initialize session settings (creates default settings if not exists)
        session_settings.load_settings(session_id)

        # Create session data
        session_data = {
            "session_id": session_id,
            "cwd": input_data.get("cwd", ""),
            "transcript_path": input_data.get("transcript_path", ""),
            "permission_mode": input_data.get("permission_mode", "default"),
            "status": "running",
            "started_at": time.time(),
            "last_activity": time.time(),
        }

        # Add session to tracking file
        hook_utils.add_session(session_data)

        # Success
        sys.exit(0)

    except Exception as e:
        print(f"Error in session-start hook: {e}", file=sys.stderr)
        sys.exit(0)  # Don't block session from starting

if __name__ == "__main__":
    main()
