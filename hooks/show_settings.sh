#!/bin/bash
# Quick settings display
# Usage: bash show_settings.sh [session_id]
# If no session_id provided, auto-detects from CWD

SESSION_ID="$1"

if [ -z "$SESSION_ID" ]; then
    SESSION_ID=$(python3 "$(dirname "$0")/get_current_session_id.py" 2>/dev/null)
fi

if [ -z "$SESSION_ID" ]; then
    echo "❌ Could not detect session ID"
    exit 1
fi

# Get settings
SETTINGS=$(python3 "$(dirname "$0")/get_session_settings.py" "$SESSION_ID" 2>/dev/null)

if [ $? -ne 0 ]; then
    echo "❌ Failed to load settings for session: $SESSION_ID"
    exit 1
fi

# Parse settings
APPROVAL_MODE=$(echo "$SETTINGS" | grep "APPROVAL_MODE=" | cut -d'=' -f2)
STOP_HOOK=$(echo "$SETTINGS" | grep "STOP_HOOK=" | cut -d'=' -f2)
NOTIFICATION_HOOK=$(echo "$SETTINGS" | grep "NOTIFICATION_HOOK=" | cut -d'=' -f2)
SESSION_START=$(echo "$SETTINGS" | grep "SESSION_START=" | cut -d'=' -f2)
SESSION_END=$(echo "$SETTINGS" | grep "SESSION_END=" | cut -d'=' -f2)
CREATED_AT=$(echo "$SETTINGS" | grep "CREATED_AT=" | cut -d'=' -f2)

# Display nicely
echo "📋 Session Settings"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Session ID: ${SESSION_ID:0:12}... (full: $SESSION_ID)"
echo "Created: $CREATED_AT"
echo ""
echo "🛡️  Approval Mode: $APPROVAL_MODE"
echo "  • ai - Smart rules + Grok-4-Fast AI fallback (recommended)"
echo "  • strict - Always ask for approval"
echo "  • disabled - No hook intervention"
echo "  • auto - Auto-approve everything (dangerous)"
echo ""
echo "🔧 Hooks Status:"
[ "$STOP_HOOK" = "true" ] && echo "  ✓ stop-hook" || echo "  ✗ stop-hook"
[ "$NOTIFICATION_HOOK" = "true" ] && echo "  ✓ notification-hook" || echo "  ✗ notification-hook"
[ "$SESSION_START" = "true" ] && echo "  ✓ session-start" || echo "  ✗ session-start"
[ "$SESSION_END" = "true" ] && echo "  ✓ session-end" || echo "  ✗ session-end"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 To change settings, tell Claude:"
echo "  • \"set approval mode to strict\""
echo "  • \"set approval mode to ai\""
echo "  • \"set approval mode to auto\""
echo "  • \"enable stop-hook\""
echo "  • \"disable notification-hook\""
