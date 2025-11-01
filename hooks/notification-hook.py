#!/usr/bin/env python3
"""
Notification Hook
Updates session status when Claude needs attention (permissions or idle)
"""

import json
import sys
import time
from pathlib import Path

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent))
import hook_utils

def main():
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        session_id = input_data.get("session_id")
        message = input_data.get("message", "")

        if not session_id:
            # No session ID, skip
            sys.exit(0)

        # Determine status based on message
        status = "running"
        if "permission" in message.lower():
            status = "needs_permission"
        elif "waiting for your input" in message.lower() or "idle" in message.lower():
            status = "waiting_for_input"

        # Update session status
        updates = {
            "status": status,
            "last_activity": time.time(),
            "last_notification": message
        }

        hook_utils.update_session(session_id, updates)

        # Success
        sys.exit(0)

    except Exception as e:
        print(f"Error in notification hook: {e}", file=sys.stderr)
        sys.exit(0)  # Don't block notifications

if __name__ == "__main__":
    main()
