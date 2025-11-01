#!/usr/bin/env python3
"""
Shared utility functions for Claude Code hooks
Handles reading/writing to the global sessions JSON file with basic file locking
"""

import json
import os
import fcntl
import time
from pathlib import Path
from typing import Dict, Any, List

# Global data file location
SESSIONS_FILE = os.path.expanduser("~/local/global/claude-sessions.json")

def acquire_lock(file_handle, timeout=5):
    """Acquire an exclusive lock on the file with timeout"""
    start_time = time.time()
    while True:
        try:
            fcntl.flock(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except IOError:
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.1)

def release_lock(file_handle):
    """Release the lock on the file"""
    fcntl.flock(file_handle, fcntl.LOCK_UN)

def read_sessions() -> Dict[str, Any]:
    """
    Read sessions from the global JSON file
    Returns empty structure if file doesn't exist
    """
    if not os.path.exists(SESSIONS_FILE):
        return {"sessions": [], "last_updated": None}

    try:
        with open(SESSIONS_FILE, 'r') as f:
            acquire_lock(f)
            try:
                data = json.load(f)
                return data
            finally:
                release_lock(f)
    except (json.JSONDecodeError, IOError):
        # If file is corrupted or can't be read, return empty structure
        return {"sessions": [], "last_updated": None}

def write_sessions(data: Dict[str, Any]) -> bool:
    """
    Write sessions to the global JSON file with file locking
    Returns True on success, False on failure
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(SESSIONS_FILE), exist_ok=True)

        # Write with atomic rename
        temp_file = SESSIONS_FILE + ".tmp"
        with open(temp_file, 'w') as f:
            acquire_lock(f)
            try:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            finally:
                release_lock(f)

        # Atomic rename
        os.rename(temp_file, SESSIONS_FILE)
        return True
    except Exception as e:
        print(f"Error writing sessions: {e}", flush=True)
        return False

def add_session(session_data: Dict[str, Any]) -> bool:
    """
    Add a new session to the tracking file
    """
    data = read_sessions()

    # Check if session already exists
    session_id = session_data.get("session_id")
    existing_sessions = [s for s in data["sessions"] if s.get("session_id") != session_id]

    # Add new session
    existing_sessions.append(session_data)

    data["sessions"] = existing_sessions
    data["last_updated"] = time.time()

    return write_sessions(data)

def remove_session(session_id: str) -> bool:
    """
    Remove a session from the tracking file
    """
    data = read_sessions()

    # Filter out the session
    data["sessions"] = [s for s in data["sessions"] if s.get("session_id") != session_id]
    data["last_updated"] = time.time()

    return write_sessions(data)

def update_session(session_id: str, updates: Dict[str, Any]) -> bool:
    """
    Update specific fields of a session
    """
    data = read_sessions()

    # Find and update the session
    for session in data["sessions"]:
        if session.get("session_id") == session_id:
            session.update(updates)
            break

    data["last_updated"] = time.time()

    return write_sessions(data)