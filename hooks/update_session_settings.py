#!/usr/bin/env python3
"""
Update session settings
Usage:
  python3 update_session_settings.py <session_id> set_approval_mode <mode>
  python3 update_session_settings.py <session_id> set_hook <hook_name> <true|false>
  python3 update_session_settings.py <session_id> fix_defaults
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))
import session_settings

def main():
    if len(sys.argv) < 3:
        print("ERROR: Invalid arguments", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    session_id = sys.argv[1]
    command = sys.argv[2]

    if command == "set_approval_mode":
        if len(sys.argv) < 4:
            print("ERROR: No mode provided", file=sys.stderr)
            sys.exit(1)
        mode = sys.argv[3]
        session_settings.set_metadata(session_id, "approval_mode", mode)
        print(f"✓ Approval mode set to: {mode}")

    elif command == "set_hook":
        if len(sys.argv) < 5:
            print("ERROR: Need hook_name and true/false", file=sys.stderr)
            sys.exit(1)
        hook_name = sys.argv[3]
        enabled = sys.argv[4].lower() in ['true', '1', 'yes']
        session_settings.set_hook_enabled(session_id, hook_name, enabled)
        print(f"✓ {hook_name}: {'enabled' if enabled else 'disabled'}")

    elif command == "fix_defaults":
        # Ensure correct defaults
        settings = session_settings.load_settings(session_id)

        # Fix approval_mode if not set or invalid
        approval_mode = settings.get("metadata", {}).get("approval_mode")
        if not approval_mode or approval_mode == "not_set":
            session_settings.set_metadata(session_id, "approval_mode", "ai")
            print("✓ Fixed approval_mode to: ai")

        # Fix hooks if any are disabled
        hooks = settings.get("hooks_enabled", {})
        for hook_name in ["stop-hook", "notification-hook", "session-start", "session-end"]:
            if not hooks.get(hook_name, False):
                session_settings.set_hook_enabled(session_id, hook_name, True)
                print(f"✓ Enabled {hook_name}")

        print("✓ Defaults fixed")

    else:
        print(f"ERROR: Unknown command: {command}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
