#!/usr/bin/env python3
"""
Get session settings for display
Usage: python3 get_session_settings.py <session_id>
"""

import sys
import json
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))
import session_settings

def main():
    if len(sys.argv) < 2:
        print("ERROR: No session_id provided", file=sys.stderr)
        sys.exit(1)

    session_id = sys.argv[1]

    # Load settings
    settings = session_settings.load_settings(session_id)

    # Extract data
    approval_mode = settings.get("metadata", {}).get("approval_mode", "not_set")
    hooks_enabled = settings.get("hooks_enabled", {})
    created_at = settings.get("created_at", "unknown")

    # Print in easy-to-parse format
    print(f"SESSION_ID={session_id}")
    print(f"APPROVAL_MODE={approval_mode}")
    print(f"CREATED_AT={created_at}")
    print(f"STOP_HOOK={'true' if hooks_enabled.get('stop-hook', False) else 'false'}")
    print(f"NOTIFICATION_HOOK={'true' if hooks_enabled.get('notification-hook', False) else 'false'}")
    print(f"SESSION_START={'true' if hooks_enabled.get('session-start', False) else 'false'}")
    print(f"SESSION_END={'true' if hooks_enabled.get('session-end', False) else 'false'}")

if __name__ == "__main__":
    main()
