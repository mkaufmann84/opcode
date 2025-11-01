#!/usr/bin/env python3
"""
Stop Hook
Updates session's last_activity timestamp when Claude finishes responding
Checks for pending todos and blocks stopping if work remains
"""

import json
import sys
import time
import os
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Any

# Add hooks directory to path
sys.path.insert(0, str(Path(__file__).parent))
import hook_utils
import session_settings


def parse_latest_todos(transcript_path: str) -> Optional[List[Dict[str, Any]]]:
    """
    Parse the transcript to find the latest todo list
    Only considers TodoWrite calls that were not rejected

    Args:
        transcript_path: Path to the session transcript JSONL file

    Returns:
        List of todo items or None if not found
    """
    if not os.path.exists(transcript_path):
        return None

    todos = None
    rejected_tool_ids = set()

    try:
        # First pass: collect all rejected tool IDs
        with open(transcript_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    message = entry.get("message", {})
                    content = message.get("content", [])

                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "tool_result":
                            # Check if this tool result indicates rejection
                            error = item.get("content")
                            tool_use_id = item.get("tool_use_id")
                            if error and "doesn't want to proceed" in str(error) and tool_use_id:
                                rejected_tool_ids.add(tool_use_id)
                except json.JSONDecodeError:
                    continue

        # Second pass: find latest non-rejected TodoWrite
        with open(transcript_path, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    message = entry.get("message", {})
                    content = message.get("content", [])

                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "tool_use" and item.get("name") == "TodoWrite":
                            tool_id = item.get("id")
                            # Only use this TodoWrite if it wasn't rejected
                            if tool_id not in rejected_tool_ids:
                                input_data = item.get("input", {})
                                extracted = input_data.get("todos")
                                if extracted is not None:  # Allow empty lists
                                    todos = extracted
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error parsing transcript: {e}", file=sys.stderr)

    return todos


def extract_todos_from_transcript_entry(entry: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """
    Extract todos from a transcript entry

    Transcript structure is:
    {
      "message": {
        "content": [
          {
            "type": "tool_use",
            "name": "TodoWrite",
            "input": {
              "todos": [...]
            }
          }
        ]
      }
    }
    """
    message = entry.get("message", {})
    content = message.get("content", [])

    for item in content:
        if isinstance(item, dict) and item.get("type") == "tool_use" and item.get("name") == "TodoWrite":
            input_data = item.get("input", {})
            todos = input_data.get("todos")
            if todos:
                return todos

    return None


def is_todo_write_tool_call(entry: Dict[str, Any]) -> bool:
    """Check if a transcript entry is a TodoWrite tool call"""
    return extract_todos_from_transcript_entry(entry) is not None


def extract_todos_from_entry(entry: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    """Extract todos list from a TodoWrite tool call entry (legacy/compatibility)"""
    return extract_todos_from_transcript_entry(entry)


def get_pending_todos(todos: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Filter todos to only include pending or in_progress items

    Args:
        todos: List of todo items

    Returns:
        List of incomplete todos
    """
    if not todos:
        return []

    return [t for t in todos if t.get("status") in ["pending", "in_progress"]]


def create_block_decision(pending_todos: List[Dict[str, Any]], max_display: int = 5) -> Dict[str, Any]:
    """
    Create a JSON decision to block Claude from stopping

    Args:
        pending_todos: List of incomplete todos
        max_display: Maximum number of todos to display in the message

    Returns:
        JSON decision object
    """
    pending_list = "\n".join([
        f"- {t.get('content', 'Unknown task')}"
        for t in pending_todos[:max_display]
    ])

    reason = f"""<system>This is an automated message. The todo list is still full. Please continue. If in the very rare circumstance user must respond, then clear the todo list and wait</system>

{len(pending_todos)} incomplete tasks remaining:
{pending_list}"""

    return {
        "decision": "block",
        "reason": reason
    }


def update_session_activity(session_id: str) -> None:
    """
    Update the session's last activity timestamp in global tracking

    Args:
        session_id: The Claude session ID
    """
    updates = {
        "last_activity": time.time(),
        "status": "running"
    }
    hook_utils.update_session(session_id, updates)


def should_skip_hook(stop_hook_active: bool) -> bool:
    """
    Determine if hook should be skipped to avoid infinite loops

    Args:
        stop_hook_active: Whether a stop hook is already active

    Returns:
        True if hook should exit early
    """
    return stop_hook_active


def main():
    """Main hook execution"""
    try:
        input_data = json.load(sys.stdin)

        session_id = input_data.get("session_id")
        transcript_path = input_data.get("transcript_path", "")

        # Check if hook is enabled for this session
        if not session_settings.is_hook_enabled(session_id, "stop-hook"):
            sys.exit(0)

        # Always check todos - rely on prompt instructions to prevent infinite loops
        stop_hook_active = False

        # Prevent infinite loop
        if should_skip_hook(stop_hook_active):
            sys.exit(0)

        # Check for pending todos
        todos = parse_latest_todos(transcript_path)
        pending_todos = get_pending_todos(todos)

        if pending_todos:
            # Block stopping and request continuation
            output = create_block_decision(pending_todos)
            print(json.dumps(output))
            sys.exit(0)

        # No pending todos - update tracking and allow stopping
        if session_id:
            update_session_activity(session_id)

        sys.exit(0)

    except Exception as e:
        print(f"Error in stop hook: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
