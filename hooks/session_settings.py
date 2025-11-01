#!/usr/bin/env python3
"""
Session Settings Manager
Provides per-session configuration for hooks and metadata
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


SETTINGS_DIR = Path.home() / "local" / "global" / "session-settings"


def get_settings_path(session_id: str) -> Path:
    """
    Get the path to the settings file for a session

    Args:
        session_id: The Claude session ID

    Returns:
        Path to the settings JSON file
    """
    return SETTINGS_DIR / f"{session_id}.json"


def get_default_settings(session_id: str) -> Dict[str, Any]:
    """
    Get default settings structure for a new session

    Args:
        session_id: The Claude session ID

    Returns:
        Default settings dictionary
    """
    return {
        "session_id": session_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "hooks_enabled": {
            "stop-hook": True,
            "notification-hook": True,
            "session-start": True,
            "session-end": True
        },
        "metadata": {
            "approval_mode": "ai"
        }
    }


def load_settings(session_id: str) -> Dict[str, Any]:
    """
    Load settings for a session, creating defaults if not found

    Args:
        session_id: The Claude session ID

    Returns:
        Settings dictionary
    """
    if not session_id:
        return get_default_settings("unknown")

    settings_path = get_settings_path(session_id)

    # Ensure directory exists
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing settings or create defaults
    if settings_path.exists():
        try:
            with open(settings_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted, return defaults
            return get_default_settings(session_id)
    else:
        # Create and save default settings
        default_settings = get_default_settings(session_id)
        save_settings(session_id, default_settings)
        return default_settings


def save_settings(session_id: str, settings: Dict[str, Any]) -> None:
    """
    Save settings for a session

    Args:
        session_id: The Claude session ID
        settings: Settings dictionary to save
    """
    if not session_id:
        return

    settings_path = get_settings_path(session_id)

    # Ensure directory exists
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

    # Update timestamp
    settings["updated_at"] = datetime.utcnow().isoformat() + "Z"

    # Save to file
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)


def is_hook_enabled(session_id: str, hook_name: str) -> bool:
    """
    Check if a specific hook is enabled for a session

    Args:
        session_id: The Claude session ID
        hook_name: Name of the hook (e.g., "stop-hook", "notification-hook")

    Returns:
        True if hook is enabled, False otherwise
    """
    settings = load_settings(session_id)
    hooks_enabled = settings.get("hooks_enabled", {})

    # Default to enabled if not specified
    return hooks_enabled.get(hook_name, True)


def set_hook_enabled(session_id: str, hook_name: str, enabled: bool) -> None:
    """
    Enable or disable a specific hook for a session

    Args:
        session_id: The Claude session ID
        hook_name: Name of the hook
        enabled: True to enable, False to disable
    """
    settings = load_settings(session_id)

    if "hooks_enabled" not in settings:
        settings["hooks_enabled"] = {}

    settings["hooks_enabled"][hook_name] = enabled
    save_settings(session_id, settings)


def get_metadata(session_id: str, key: str, default: Any = None) -> Any:
    """
    Get a metadata value for a session

    Args:
        session_id: The Claude session ID
        key: Metadata key
        default: Default value if key not found

    Returns:
        Metadata value or default
    """
    settings = load_settings(session_id)
    metadata = settings.get("metadata", {})
    return metadata.get(key, default)


def set_metadata(session_id: str, key: str, value: Any) -> None:
    """
    Set a metadata value for a session

    Args:
        session_id: The Claude session ID
        key: Metadata key
        value: Value to set
    """
    settings = load_settings(session_id)

    if "metadata" not in settings:
        settings["metadata"] = {}

    settings["metadata"][key] = value
    save_settings(session_id, settings)


def clear_settings(session_id: str) -> None:
    """
    Clear all settings for a session (reset to defaults)

    Args:
        session_id: The Claude session ID
    """
    if not session_id:
        return

    settings_path = get_settings_path(session_id)

    if settings_path.exists():
        settings_path.unlink()

    # Recreate with defaults
    default_settings = get_default_settings(session_id)
    save_settings(session_id, default_settings)


def list_all_sessions() -> list[Dict[str, Any]]:
    """
    List all sessions with settings

    Returns:
        List of settings dictionaries
    """
    if not SETTINGS_DIR.exists():
        return []

    sessions = []
    for settings_file in SETTINGS_DIR.glob("*.json"):
        try:
            with open(settings_file, 'r') as f:
                sessions.append(json.load(f))
        except (json.JSONDecodeError, IOError):
            continue

    # Sort by creation time (newest first)
    sessions.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    return sessions


if __name__ == "__main__":
    # Test functionality
    test_session_id = "test-session-123"

    print(f"Testing session settings for: {test_session_id}")

    # Load default settings
    settings = load_settings(test_session_id)
    print(f"\nDefault settings: {json.dumps(settings, indent=2)}")

    # Test hook enabled/disabled
    print(f"\nIs stop-hook enabled? {is_hook_enabled(test_session_id, 'stop-hook')}")
    set_hook_enabled(test_session_id, 'stop-hook', False)
    print(f"After disabling: {is_hook_enabled(test_session_id, 'stop-hook')}")

    # Test metadata
    set_metadata(test_session_id, "project_name", "test-project")
    set_metadata(test_session_id, "approval_mode", "strict")
    print(f"\nProject name: {get_metadata(test_session_id, 'project_name')}")
    print(f"Approval mode: {get_metadata(test_session_id, 'approval_mode')}")

    # Show final settings
    final_settings = load_settings(test_session_id)
    print(f"\nFinal settings: {json.dumps(final_settings, indent=2)}")

    # Cleanup
    clear_settings(test_session_id)
    print(f"\nSettings cleared")
