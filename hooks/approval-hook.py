#!/usr/bin/env python3
"""
Approval Hook (PreToolUse)
Uses Grok-4-Fast to judge whether tool operations should be auto-approved, denied, or require user confirmation
"""

import json
import sys
import os
from pathlib import Path

# Add paths for imports
sys.path.insert(0, "/Users/max/local/opcode/utils")
sys.path.insert(0, str(Path(__file__).parent))

# Load .env from opcode directory
from dotenv import load_dotenv
load_dotenv("/Users/max/local/opcode/.env")

from llm_utils import LangChainLLMClient, LangChainLLMConfig, build_messages
import session_settings


def is_safe_operation(tool_name: str, tool_input: dict, cwd: str) -> tuple[bool, str]:
    """
    Apply smart default rules to determine if an operation is safe

    Args:
        tool_name: Name of the tool being called
        tool_input: Input parameters for the tool
        cwd: Current working directory

    Returns:
        Tuple of (is_safe, reason)
    """
    # Always allow Read operations (read-only)
    if tool_name == "Read":
        return (True, "Read operation - safe (read-only)")

    # Always allow Grep operations (read-only)
    if tool_name == "Grep":
        return (True, "Grep operation - safe (read-only)")

    # Always allow Glob operations (read-only)
    if tool_name == "Glob":
        return (True, "Glob operation - safe (read-only)")

    # Always allow core Claude Code tools
    core_claude_tools = ["TodoWrite", "Task", "Skill", "SlashCommand", "AskUserQuestion", "ExitPlanMode"]
    if tool_name in core_claude_tools:
        return (True, f"{tool_name} - core Claude Code tool (safe)")

    # Check for safe temporary directory writes
    if tool_name in ["Write", "Edit"]:
        file_path = tool_input.get("file_path", "")

        # Allow writes to /tmp, /var/tmp, and user's temp directories
        safe_temp_dirs = ["/tmp/", "/var/tmp/", "/private/tmp/"]

        if any(file_path.startswith(temp_dir) for temp_dir in safe_temp_dirs):
            return (True, f"Write to temporary directory - safe ({file_path})")

    # Not a recognized safe operation
    return (False, "Operation requires review")


def judge_with_grok(tool_name: str, tool_input: dict, cwd: str) -> str:
    """
    Use Grok-4-Fast to judge the safety of a tool operation

    Args:
        tool_name: Name of the tool being called
        tool_input: Input parameters for the tool
        cwd: Current working directory

    Returns:
        One of: "allow", "deny", "ask"
    """
    try:
        config = LangChainLLMConfig(
            model="grok-4-fast",
            temperature=0.1,
            max_tokens=50
        )

        client = LangChainLLMClient(config)

        # Build judgment prompt
        prompt = f"""You are a security advisor evaluating tool use in a coding assistant.

Tool: {tool_name}
Input: {json.dumps(tool_input, indent=2)}
Working Directory: {cwd}

Evaluate this operation and respond with ONE word only:
- ALLOW: Safe operation, auto-approve (e.g., read-only operations, safe commands)
- DENY: Dangerous/destructive, block it (e.g., rm -rf, DROP TABLE, deleting critical files)
- ASK: Unclear risk, let user decide (e.g., modifying sensitive files, complex operations)

Consider:
- Is this read-only? → ALLOW
- Is this destructive or irreversible? → DENY or ASK
- Does it modify critical files (.env, .git/, credentials)? → ASK
- Is the risk low and context clear? → ALLOW

Response (ONE WORD ONLY):"""

        messages = build_messages(None, prompt)
        response = client.chat(messages).strip().upper()

        # Validate response
        if response in ["ALLOW", "DENY", "ASK"]:
            return response.lower()

        # If unexpected response, default to safe
        return "ask"

    except Exception as e:
        print(f"Error calling Grok: {e}", file=sys.stderr)
        # On error, default to asking user
        return "ask"


def main():
    """Main hook execution"""
    try:
        # Read hook input
        input_data = json.load(sys.stdin)

        session_id = input_data.get("session_id")
        tool_name = input_data.get("tool_name")
        tool_input = input_data.get("tool_input", {})
        cwd = input_data.get("cwd", "")

        # Check session settings for approval mode
        approval_mode = session_settings.get_metadata(session_id, "approval_mode", "ai")

        # Disabled mode - no hook intervention
        if approval_mode == "disabled":
            sys.exit(0)

        # Strict mode - always ask for manual approval
        if approval_mode == "strict":
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": "Strict mode: Manual approval required for all operations"
                }
            }
            print(json.dumps(output))
            sys.exit(0)

        # Auto mode - auto-approve everything (bypass permissions)
        if approval_mode == "auto":
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "permissionDecisionReason": "Auto mode: Bypassing all permission checks"
                }
            }
            print(json.dumps(output))
            sys.exit(0)

        # AI mode - use Grok to judge
        if approval_mode == "ai":
            # First check if it's a safe operation by smart rules (faster)
            is_safe, reason = is_safe_operation(tool_name, tool_input, cwd)
            if is_safe:
                # Use smart rules for known safe operations (no API call needed)
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "allow",
                        "permissionDecisionReason": f"AI mode: {reason} (bypassing Grok)"
                    }
                }
                print(json.dumps(output))
                sys.exit(0)

            # Not a known safe operation, use Grok to judge
            decision = judge_with_grok(tool_name, tool_input, cwd)

            reasons = {
                "allow": f"Grok judged this {tool_name} operation as safe - auto-approved",
                "deny": f"Grok judged this {tool_name} operation as dangerous - blocked",
                "ask": f"Grok needs user input to judge this {tool_name} operation"
            }

            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": reasons.get(decision, "Unknown")
                }
            }
            print(json.dumps(output))
            sys.exit(0)

        # Unknown mode - default to asking
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": f"Unknown approval mode '{approval_mode}' - defaulting to ask"
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        # On any error, fail safely by asking user
        print(f"Error in approval hook: {e}", file=sys.stderr)
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": f"Hook error: {str(e)} - defaulting to ask"
            }
        }
        print(json.dumps(output))
        sys.exit(0)


if __name__ == "__main__":
    main()
