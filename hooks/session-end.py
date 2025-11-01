#!/usr/bin/env python3
"""
SessionEnd Hook
Removes a Claude Code session when it ends
"""

import json
import sys
from pathlib import Path

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent))
import hook_utils

def main():
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        session_id = input_data.get("session_id")
        if not session_id:
            # No session ID, skip
            sys.exit(0)

        # Remove session from tracking file
        hook_utils.remove_session(session_id)

        # Success
        sys.exit(0)

    except Exception as e:
        print(f"Error in session-end hook: {e}", file=sys.stderr)
        sys.exit(0)  # Don't block session from ending

if __name__ == "__main__":
    main()
