# Opcode Web Server - Complete Reference

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Reference](#api-reference)
4. [WebSocket Protocol](#websocket-protocol)
5. [Session Management](#session-management)
6. [Process Lifecycle](#process-lifecycle)
7. [Event System](#event-system)
8. [Critical Bugs & Issues](#critical-bugs--issues)
9. [Desktop vs Web Differences](#desktop-vs-web-differences)
10. [Security Considerations](#security-considerations)
11. [Deployment Guide](#deployment-guide)
12. [Performance & Scaling](#performance--scaling)
13. [Testing Guide](#testing-guide)
14. [Client Examples](#client-examples)

---

## Overview

The `opcode-web` binary provides browser and mobile access to Opcode functionality through a REST API and WebSocket interface. It allows running Claude Code sessions from any device with a web browser while maintaining compatibility with the desktop UI.

### Key Features

- WebSocket-based real-time Claude execution with streaming output
- REST API for project/session management
- Browser-compatible event system using DOM events
- Session tracking and management
- CORS-enabled for phone/tablet access

### Current Status

**Working**: Single-session usage, basic Claude execution, project browsing
**Broken**: Multi-session isolation, process cancellation, stderr handling

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser/Mobile UI                         │
│  • React/TypeScript Frontend (same as desktop)                   │
│  • WebSocket Client (apiAdapter.ts)                             │
│  • DOM Event Listeners (ClaudeCodeSession.tsx)                  │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    │ WebSocket (/ws/claude)
                    │ REST API (/api/*)
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Axum Web Server (Rust)                        │
│  • web_server.rs - Route handlers                               │
│  • AppState - Session tracking (HashMap)                        │
│  • CORS Layer - Cross-origin support                            │
│  • ServeDir - Static file serving                               │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    │ tokio::process::Command
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Binary Subprocess                      │
│  • claude-code CLI                                              │
│  • Spawned with --output-format stream-json                    │
│  • stdout captured and streamed line-by-line                   │
│  • stderr NOT CAPTURED (BUG #3)                                 │
└─────────────────────────────────────────────────────────────────┘
```

### File Structure

```
src-tauri/
├── src/
│   ├── web_main.rs          # Entry point for opcode-web binary
│   ├── web_server.rs        # Main web server implementation (848 lines)
│   ├── commands/
│   │   └── claude.rs        # Shared Claude command logic (desktop)
│   └── process/
│       └── registry.rs      # Process tracking (desktop only)
└── Cargo.toml               # Defines both opcode and opcode-web binaries

src/
├── lib/
│   └── apiAdapter.ts        # Environment detection & WebSocket client
└── components/
    ├── ClaudeCodeSession.tsx
    └── claude-code-session/
        └── useClaudeMessages.ts  # Event handling hook
```

### Key Data Structures

#### AppState (web_server.rs)

```rust
pub struct AppState {
    pub active_sessions: Arc<Mutex<HashMap<String, tokio::sync::mpsc::Sender<String>>>>
}
```

**Purpose**: Track active WebSocket sessions for sending Claude output
**Issue**: Does NOT store Child process handles - cannot cancel processes

#### ClaudeExecutionRequest (WebSocket message)

```rust
pub struct ClaudeExecutionRequest {
    pub project_path: String,
    pub prompt: String,
    pub model: Option<String>,
    pub session_id: Option<String>,
    pub command_type: String, // "execute", "continue", or "resume"
}
```

---

## API Reference

### REST Endpoints

#### Projects & Sessions

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/api/projects` | GET | List all Claude projects | - | `ApiResponse<Vec<Project>>` |
| `/api/projects/{project_id}/sessions` | GET | Get sessions for project | Path: `project_id` | `ApiResponse<Vec<Session>>` |
| `/api/sessions/{session_id}/history/{project_id}` | GET | Load session history (JSONL) | Path: `session_id`, `project_id` | `ApiResponse<Vec<serde_json::Value>>` |
| `/api/sessions/new` | GET | Open new session | - | `ApiResponse<String>` (session_id) |
| `/api/sessions/running` | GET | List running Claude sessions | - | `ApiResponse<Vec<serde_json::Value>>` (empty in web mode) |

**Example - List Projects:**

```bash
curl http://localhost:8080/api/projects
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "id": "-Users-max-local-opcode",
      "path": "/Users/max/local/opcode",
      "sessions": ["uuid-1", "uuid-2"],
      "created_at": 1729468800,
      "most_recent_session": 1729555200
    }
  ],
  "error": null
}
```

#### Settings & Configuration

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/settings/claude` | GET | Get Claude settings | `ApiResponse<serde_json::Value>` |
| `/api/settings/claude/version` | GET | Check Claude version | `ApiResponse<serde_json::Value>` |
| `/api/settings/claude/installations` | GET | List Claude installations | `ApiResponse<Vec<ClaudeInstallation>>` |
| `/api/settings/system-prompt` | GET | Get system prompt | `ApiResponse<String>` |

**Default Settings Response:**

```json
{
  "success": true,
  "data": {
    "data": {
      "model": "claude-3-5-sonnet-20241022",
      "max_tokens": 8192,
      "temperature": 0.0,
      "auto_save": true,
      "theme": "dark"
    }
  }
}
```

#### Claude Execution (Stub Endpoints)

| Endpoint | Method | Description | Status |
|----------|--------|-------------|--------|
| `/api/sessions/execute` | GET | Execute Claude (stub) | Returns error - use WebSocket |
| `/api/sessions/continue` | GET | Continue Claude (stub) | Returns error - use WebSocket |
| `/api/sessions/resume` | GET | Resume Claude (stub) | Returns error - use WebSocket |
| `/api/sessions/{sessionId}/cancel` | GET | Cancel execution | **BROKEN** - logs only, doesn't cancel |
| `/api/sessions/{sessionId}/output` | GET | Get session output | Returns "Output available via WebSocket only" |

**Why Stubs?** The actual execution happens via WebSocket (`/ws/claude`), not REST API. These endpoints exist for API completeness but redirect users to WebSocket.

#### Agents, Usage, MCP (Mock Endpoints)

These endpoints return empty arrays or default values in web mode:

- `/api/agents` - Returns `[]`
- `/api/usage` - Returns `[]`
- `/api/slash-commands` - Returns `[]`
- `/api/mcp/servers` - Returns `[]`

**Reason**: These features require database access (`opcode.db`) which is not implemented in web server mode.

#### Static Files

- `/` - Serves `dist/index.html`
- `/index.html` - Serves `dist/index.html`
- `/assets/*` - Serves `dist/assets/` (Vite build output)
- `/vite.svg` - Serves `dist/vite.svg`

---

## WebSocket Protocol

### Connection

**URL**: `ws://localhost:8080/ws/claude` (or `wss://` for HTTPS)

**Upgrade Request**:
```http
GET /ws/claude HTTP/1.1
Host: localhost:8080
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

### Message Format

#### Client → Server

**Execute New Session:**
```json
{
  "command_type": "execute",
  "project_path": "/Users/max/local/opcode",
  "prompt": "Add a hello world function",
  "model": "claude-3-5-sonnet-20241022",
  "session_id": null
}
```

**Continue Session:**
```json
{
  "command_type": "continue",
  "project_path": "/Users/max/local/opcode",
  "prompt": "Now add tests for it",
  "model": "claude-3-5-sonnet-20241022",
  "session_id": null
}
```

**Resume Session:**
```json
{
  "command_type": "resume",
  "project_path": "/Users/max/local/opcode",
  "prompt": "Continue from where we left off",
  "model": "claude-3-5-sonnet-20241022",
  "session_id": "existing-uuid-here"
}
```

#### Server → Client

**Start Message:**
```json
{
  "type": "start",
  "message": "Starting Claude execution..."
}
```

**Output Message (Claude stream-json line):**
```json
{
  "type": "output",
  "content": "{\"type\":\"start\",\"session_id\":\"uuid\",...}"
}
```

**Note**: The `content` field is a **JSON string** that needs to be parsed again to get the actual Claude message.

**Completion Message:**
```json
{
  "type": "completion",
  "status": "success"
}
```

**Error Message:**
```json
{
  "type": "error",
  "message": "Failed to spawn Claude: binary not found"
}
```

### Session Lifecycle

1. **Client connects** to `/ws/claude`
2. **Server generates** UUID for WebSocket session
3. **Server stores** sender channel in `AppState.active_sessions`
4. **Client sends** execution request (JSON)
5. **Server spawns** Claude subprocess
6. **Server streams** stdout line-by-line as `output` messages
7. **Client dispatches** DOM events (`claude-output`)
8. **Process completes** - server sends `completion` message
9. **WebSocket closes** - server removes session from `active_sessions`

### WebSocket Error Handling

**Connection Error:**
```typescript
ws.onerror = (error) => {
  // Dispatches 'claude-error' DOM event
  window.dispatchEvent(new CustomEvent('claude-error', {
    detail: 'WebSocket connection failed'
  }));
};
```

**Unexpected Close:**
```typescript
ws.onclose = (event) => {
  if (event.code !== 1000 && event.code !== 1001) {
    // Dispatches 'claude-complete' with failure
    window.dispatchEvent(new CustomEvent('claude-complete', {
      detail: false
    }));
  }
};
```

---

## Session Management

### Session ID Confusion (BUG #5)

The web server has **two different session ID concepts**:

1. **WebSocket Session ID** - Generated by server (`uuid::Uuid::new_v4()`)
2. **Claude Session ID** - Passed by client in `session_id` field

**Problem**: These are not mapped or synchronized.

**Code Evidence** (web_server.rs:259):
```rust
async fn claude_websocket_handler(socket: WebSocket, state: AppState) {
    let session_id = uuid::Uuid::new_v4().to_string(); // Server-generated
    // ...

    // Later, client sends:
    // { "session_id": "user-provided-uuid", ... }
    // These don't match!
}
```

### Session Storage

**What's Stored**:
```rust
HashMap<String, tokio::sync::mpsc::Sender<String>>
```

- **Key**: WebSocket session ID (server-generated UUID)
- **Value**: Channel sender for pushing messages to WebSocket

**What's NOT Stored** (causes BUG #2):
- Child process handles
- PIDs
- Session metadata
- Relationship to Claude session IDs

**Comparison with Desktop** (process/registry.rs):
```rust
pub struct ProcessHandle {
    pub info: ProcessInfo,
    pub child: Arc<Mutex<Option<Child>>>,  // ← HAS THIS
    pub live_output: Arc<Mutex<String>>,
}
```

Desktop stores `Child` handles, web server doesn't.

### Session Cleanup

**When WebSocket Closes** (web_server.rs:430):
```rust
// Clean up session
{
    let mut sessions = state.active_sessions.lock().await;
    sessions.remove(&session_id);
}
```

**Issue**: Removes sender channel but **does NOT terminate child process**. Process continues running in background.

---

## Process Lifecycle

### Process Spawning

**Function**: `execute_claude_command()`, `continue_claude_command()`, `resume_claude_command()`

**Code** (web_server.rs:453-568):
```rust
async fn execute_claude_command(
    project_path: String,
    prompt: String,
    model: String,
    session_id: String,
    state: AppState,
) -> Result<(), String> {
    // 1. Find Claude binary
    let claude_path = find_claude_binary_web()?;

    // 2. Create command
    let mut cmd = Command::new(&claude_path);
    cmd.args([
        "-p", &prompt,
        "--model", &model,
        "--output-format", "stream-json",
        "--verbose",
        "--dangerously-skip-permissions"
    ]);
    cmd.current_dir(&project_path);
    cmd.stdout(std::process::Stdio::piped());
    cmd.stderr(std::process::Stdio::piped());  // ← PIPED BUT NOT READ

    // 3. Spawn process
    let mut child = cmd.spawn()?;

    // 4. Stream stdout only
    let stdout = child.stdout.take()?;
    let stdout_reader = BufReader::new(stdout);

    // 5. Read line by line
    let mut lines = stdout_reader.lines();
    while let Ok(Some(line)) = lines.next_line().await {
        send_to_session(&state, &session_id, json!({
            "type": "output",
            "content": line  // ← Raw JSON string from Claude
        }).to_string()).await;
    }

    // 6. Wait for exit
    let exit_status = child.wait().await?;

    // 7. Process handle is DROPPED - no storage
    Ok(())
}
```

### stdout vs stderr

**Current Behavior**:
- `cmd.stdout(Stdio::piped())` - ✅ Captured and streamed
- `cmd.stderr(Stdio::piped())` - ❌ Piped but **never read**

**Missing Code**:
```rust
// This code does NOT exist in web_server.rs
let stderr = child.stderr.take()?;
let stderr_reader = BufReader::new(stderr);
let mut stderr_lines = stderr_reader.lines();
while let Ok(Some(line)) = stderr_lines.next_line().await {
    // Should emit claude-error event
}
```

### Process Cancellation

**Desktop Implementation** (commands/claude.rs:1019-1119):
```rust
pub async fn cancel_claude_execution(app: AppHandle, session_id: Option<String>) -> Result<(), String> {
    // Method 1: Find in ProcessRegistry
    let registry = app.state::<ProcessRegistryState>();
    if let Some(process_info) = registry.0.get_claude_session_by_id(&sid)? {
        registry.0.kill_process(process_info.run_id).await?;
    }

    // Method 2: Check ClaudeProcessState
    let claude_state = app.state::<ClaudeProcessState>();
    let mut current_process = claude_state.current_process.lock().await;
    if let Some(mut child) = current_process.take() {
        child.kill().await?;
    }

    // Method 3: System kill by PID
    std::process::Command::new("kill")
        .args(["-KILL", &pid.to_string()])
        .output()?;
}
```

**Web Implementation** (web_server.rs:236-241):
```rust
async fn cancel_claude_execution(Path(sessionId): Path<String>) -> Json<ApiResponse<()>> {
    println!("[TRACE] Cancel request for session: {}", sessionId);
    Json(ApiResponse::success(())) // ← DOES NOTHING
}
```

**Impact**: Processes continue running until completion. Users cannot stop long-running or stuck processes.

---

## Event System

### Desktop vs Web Event Flow

#### Desktop (Tauri)

```
Claude Output → Tauri Event System → emit("claude-output:uuid") → Frontend
```

Code (commands/claude.rs):
```rust
let _ = app.emit(&format!("claude-output:{}", session_id), &line);
let _ = app.emit("claude-output", &line);
```

Frontend receives via `@tauri-apps/api/event`:
```typescript
import { listen } from '@tauri-apps/api/event';
await listen(`claude-output:${sessionId}`, handleOutput);
```

#### Web Server

```
WebSocket Message → apiAdapter.ts → DOM Event → Frontend
```

Code (apiAdapter.ts:324-342):
```typescript
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  if (message.type === 'output') {
    const claudeMessage = JSON.parse(message.content);

    // Only dispatches GENERIC event
    window.dispatchEvent(new CustomEvent('claude-output', {
      detail: claudeMessage
    }));
    // ❌ Does NOT dispatch session-specific event:
    // window.dispatchEvent(new CustomEvent(`claude-output:${sessionId}`, {...}));
  }
};
```

Frontend listens via DOM events:
```typescript
const listen = (eventName: string, callback: Function) => {
  const handler = (event: any) => callback({ payload: event.detail });
  window.addEventListener(eventName, handler);
  return () => window.removeEventListener(eventName, handler);
};
```

### Event Types

| Event Name | Desktop | Web | Purpose |
|------------|---------|-----|---------|
| `claude-output` | ✅ | ✅ | Generic output (all sessions) |
| `claude-output:${sessionId}` | ✅ | ❌ | Session-specific output |
| `claude-complete` | ✅ | ✅ | Execution completed |
| `claude-complete:${sessionId}` | ✅ | ❌ | Session-specific completion |
| `claude-error` | ✅ | ✅ | Generic error |
| `claude-error:${sessionId}` | ✅ | ❌ | Session-specific error |
| `claude-cancelled` | ✅ | ❌ | Process was cancelled |
| `claude-cancelled:${sessionId}` | ✅ | ❌ | Session-specific cancellation |

### Session-Scoped Events (BUG #1)

**Expected Frontend Usage** (useClaudeMessages.ts):
```typescript
await listen(`claude-output:${sessionId}`, handleOutput);
await listen(`claude-error:${sessionId}`, handleError);
await listen(`claude-complete:${sessionId}`, handleComplete);
```

**What Web Server Dispatches**:
```typescript
window.dispatchEvent(new CustomEvent('claude-output', { detail }));
window.dispatchEvent(new CustomEvent('claude-complete', { detail }));
window.dispatchEvent(new CustomEvent('claude-error', { detail }));
```

**Result**: All sessions receive all events. Session isolation broken.

---

## Critical Bugs & Issues

### BUG #1: Session-Scoped Event Dispatching BROKEN 🔴

**Priority**: CRITICAL
**Impact**: Multiple sessions interfere with each other
**Affects**: All concurrent users

**Problem**: Web server only dispatches generic events (`claude-output`), not session-specific events (`claude-output:${sessionId}`).

**Root Cause**:
1. Frontend expects session-scoped events for isolation
2. Web server dispatches only generic DOM events
3. All browser tabs/sessions receive all events

**Evidence**:
```typescript
// apiAdapter.ts:337 - Only generic event
window.dispatchEvent(new CustomEvent('claude-output', { detail: claudeMessage }));

// useClaudeMessages.ts:141 - Expects session-specific
await tauriListen(`claude-output:${sessionId}`, handleOutput);
```

**Workaround**: Use only one session at a time.

**Fix Difficulty**: MEDIUM
**Fix Approach**:
1. Extract session_id from Claude output (`content` field has `session_id`)
2. Dispatch both generic and session-specific events:
   ```typescript
   const sessionId = claudeMessage.session_id;
   window.dispatchEvent(new CustomEvent('claude-output', { detail: claudeMessage }));
   window.dispatchEvent(new CustomEvent(`claude-output:${sessionId}`, { detail: claudeMessage }));
   ```
3. Update WebSocket handler to track client-provided session_id

**Testing**: Open two browser tabs, start sessions in both, verify events don't cross-contaminate.

---

### BUG #2: Process Cancellation NOT IMPLEMENTED 🔴

**Priority**: CRITICAL
**Impact**: Users cannot stop running processes
**Affects**: All users, all sessions

**Problem**: Cancel button does nothing. Processes continue running until completion.

**Root Cause**: `AppState` doesn't store Child process handles.

**Evidence**:
```rust
// web_server.rs:62 - No child storage
pub struct AppState {
    pub active_sessions: Arc<Mutex<HashMap<String, tokio::sync::mpsc::Sender<String>>>>
    // ❌ Missing: pub active_processes: Arc<Mutex<HashMap<String, Child>>>
}

// web_server.rs:236 - Cancel does nothing
async fn cancel_claude_execution(Path(sessionId): Path<String>) -> Json<ApiResponse<()>> {
    println!("[TRACE] Cancel request for session: {}", sessionId);
    Json(ApiResponse::success(())) // ← Just logs and returns
}
```

**Impact**:
- Long-running processes cannot be stopped
- Stuck processes waste resources
- User has no control after starting execution

**Workaround**: Restart entire web server (`pkill opcode-web`).

**Fix Difficulty**: MEDIUM-HIGH
**Fix Approach**:
1. Modify `AppState` to store process handles:
   ```rust
   pub struct AppState {
       pub active_sessions: Arc<Mutex<HashMap<String, Sender<String>>>>,
       pub active_processes: Arc<Mutex<HashMap<String, Child>>>, // ← ADD
   }
   ```
2. Store child in HashMap when spawning:
   ```rust
   let mut child = cmd.spawn()?;
   state.active_processes.lock().await.insert(session_id.clone(), child);
   ```
3. Implement cancel:
   ```rust
   async fn cancel_claude_execution(Path(sessionId): Path<String>, AxumState(state): AxumState<AppState>) {
       if let Some(mut child) = state.active_processes.lock().await.remove(&sessionId) {
           child.kill().await?;
       }
   }
   ```
4. Clean up on completion/error

**Testing**: Start long session, click cancel, verify process terminates.

---

### BUG #3: stderr Not Captured 🟡

**Priority**: HIGH
**Impact**: Error messages from Claude not displayed
**Affects**: All users

**Problem**: Web server only captures stdout, not stderr. Claude errors go to void.

**Root Cause**: stderr is piped but never read.

**Evidence**:
```rust
// web_server.rs:499
cmd.stderr(std::process::Stdio::piped()); // ← Piped

// web_server.rs:516-538 - Only stdout is read
let stdout = child.stdout.take()?;
let stdout_reader = BufReader::new(stdout);
let mut lines = stdout_reader.lines();
while let Ok(Some(line)) = lines.next_line().await {
    // Send stdout
}
// ❌ stderr is NEVER read
```

**Impact**:
- Users don't see Claude errors (e.g., "file not found", "permission denied")
- Debugging is impossible
- Silent failures

**Workaround**: Check terminal logs where `opcode-web` was started (stderr goes there).

**Fix Difficulty**: MEDIUM
**Fix Approach**:
1. Spawn separate task to read stderr:
   ```rust
   let stderr = child.stderr.take()?;
   let stderr_reader = BufReader::new(stderr);
   let session_id_clone = session_id.clone();
   let state_clone = state.clone();

   tokio::spawn(async move {
       let mut lines = stderr_reader.lines();
       while let Ok(Some(line)) = lines.next_line().await {
           send_to_session(&state_clone, &session_id_clone, json!({
               "type": "error",
               "content": line
           }).to_string()).await;
       }
   });
   ```
2. Update frontend to handle `type: "error"` messages
3. Dispatch `claude-error` DOM events

**Testing**: Trigger Claude error (invalid path), verify error shown in UI.

---

### BUG #4: Missing claude-cancelled Events 🟡

**Priority**: MEDIUM
**Impact**: Inconsistent behavior between desktop and web
**Affects**: UI state management

**Problem**: Desktop emits `claude-cancelled` events, web server doesn't.

**Root Cause**: Web server doesn't implement cancellation at all (see BUG #2).

**Evidence**:
```rust
// commands/claude.rs:1136 (Desktop)
let _ = app.emit(&format!("claude-cancelled:{}", sid), true);
let _ = app.emit("claude-cancelled", true);

// web_server.rs - No equivalent code exists
```

**Impact**:
- UI doesn't update properly when process is cancelled
- Cancel button appears to work but doesn't emit events
- Frontend state gets confused

**Workaround**: None (cancellation doesn't work at all).

**Fix Difficulty**: LOW (once BUG #2 is fixed)
**Fix Approach**:
1. After implementing cancellation (BUG #2 fix)
2. Dispatch cancelled events:
   ```typescript
   window.dispatchEvent(new CustomEvent('claude-cancelled', { detail: true }));
   window.dispatchEvent(new CustomEvent(`claude-cancelled:${sessionId}`, { detail: true }));
   ```
3. Update UI to handle these events

**Testing**: Cancel session, verify UI resets to prompt state.

---

### BUG #5: WebSocket Session ID Mapping 🟡

**Priority**: MEDIUM
**Impact**: Session ID confusion, potential tracking issues
**Affects**: Session management

**Problem**: Server generates its own session IDs, client passes different session IDs in requests. No mapping between them.

**Root Cause**: Two separate ID systems:

**Evidence**:
```rust
// web_server.rs:259 - Server generates UUID
let session_id = uuid::Uuid::new_v4().to_string();

// Client sends different ID in request:
{
  "session_id": "client-provided-uuid", // ← Different from WebSocket session_id
  "command_type": "resume"
}
```

**Impact**:
- Cannot correlate WebSocket session with Claude session
- Resume functionality may be broken
- Cancellation by session_id won't work

**Workaround**: Don't use resume functionality in web mode.

**Fix Difficulty**: LOW
**Fix Approach**:
1. Use client-provided session_id instead of generating new one:
   ```rust
   // Parse request first to get session_id
   let request: ClaudeExecutionRequest = serde_json::from_str(&text)?;
   let session_id = request.session_id.unwrap_or_else(|| uuid::Uuid::new_v4().to_string());
   ```
2. Store bidirectional mapping if needed
3. Use consistent IDs throughout

**Testing**: Resume session, verify same session_id used for WebSocket and Claude.

---

### BUG #6: No Process Cleanup on WebSocket Disconnect 🔴

**Priority**: CRITICAL
**Impact**: Resource leak, zombie processes
**Affects**: All users, server stability

**Problem**: When WebSocket disconnects, session is removed from HashMap but child process keeps running.

**Root Cause**: No link between WebSocket session and Child process.

**Evidence**:
```rust
// web_server.rs:430 - Only removes sender channel
{
    let mut sessions = state.active_sessions.lock().await;
    sessions.remove(&session_id); // ← Channel removed, process still running
}

forward_task.abort(); // ← Only aborts forward task, not Claude process
```

**Impact**:
- User closes browser tab → process continues running
- User loses connection → process becomes orphan
- Long sessions can accumulate and consume resources
- Server eventually runs out of memory/processes

**Workaround**: Manually kill processes: `ps aux | grep claude | awk '{print $2}' | xargs kill`

**Fix Difficulty**: MEDIUM (requires BUG #2 fix first)
**Fix Approach**:
1. Store process handles in AppState (BUG #2 fix)
2. In WebSocket cleanup:
   ```rust
   // Kill child process
   if let Some(mut child) = state.active_processes.lock().await.remove(&session_id) {
       let _ = child.kill().await;
   }

   // Remove sender
   state.active_sessions.lock().await.remove(&session_id);
   ```
3. Add graceful shutdown timeout before force kill

**Testing**: Start session, close browser tab, verify `ps aux | grep claude` shows process terminated.

---

### BUG #7: Binary Detection Path Hardcoded 🟡

**Priority**: LOW
**Impact**: Web server may not find Claude binary on some systems
**Affects**: Linux users, non-standard installations

**Problem**: Bundled binary path is hardcoded for Linux x86_64.

**Evidence**:
```rust
// web_server.rs:26
let bundled_binary = "src-tauri/binaries/claude-code-x86_64-unknown-linux-gnu";
```

**Impact**:
- Won't work on macOS (aarch64-apple-darwin)
- Won't work on Windows
- Won't work on ARM Linux
- Fails if run from different directory

**Workaround**: Ensure `claude` is in system PATH.

**Fix Difficulty**: LOW
**Fix Approach**:
1. Use same logic as desktop (`claude_binary::find_claude_binary()`)
2. Detect platform at runtime
3. Check multiple bundled binary paths
4. Use relative path from binary location, not CWD

**Testing**: Run on macOS, Windows, Linux (ARM and x86_64), verify binary found.

---

### BUG #8: CORS Allows All Origins 🟡

**Priority**: MEDIUM (security)
**Impact**: Potential security risk in production
**Affects**: Production deployments

**Problem**: CORS is configured to allow all origins, methods, and headers.

**Evidence**:
```rust
// web_server.rs:776
let cors = CorsLayer::new()
    .allow_origin(Any)      // ← Allows ANY origin
    .allow_methods([...])
    .allow_headers(Any);    // ← Allows ANY headers
```

**Impact**:
- Any website can make requests to your Opcode server
- CSRF attacks possible
- Data exfiltration risk
- Good for development, bad for production

**Workaround**: Run behind reverse proxy with strict CORS.

**Fix Difficulty**: LOW
**Fix Approach**:
1. Add configuration option for allowed origins
2. In production, restrict to specific domains:
   ```rust
   let cors = if cfg!(debug_assertions) {
       CorsLayer::permissive()
   } else {
       CorsLayer::new()
           .allow_origin("https://yourdomain.com".parse::<HeaderValue>()?)
           .allow_methods([Method::GET, Method::POST])
   };
   ```
3. Add authentication/authorization

**Testing**: Attempt cross-origin request from unauthorized domain, verify rejection.

---

### BUG #9: No Rate Limiting 🟢

**Priority**: LOW (enhancement)
**Impact**: Potential DoS, resource exhaustion
**Affects**: Public-facing deployments

**Problem**: No rate limiting on API endpoints or WebSocket connections.

**Impact**:
- User can spawn unlimited Claude processes
- Rapid API calls can exhaust resources
- No protection against abuse

**Workaround**: Use reverse proxy with rate limiting (nginx, Caddy).

**Fix Difficulty**: MEDIUM
**Fix Approach**:
1. Add rate limiting middleware (tower-rate-limit)
2. Limit concurrent processes per IP/user
3. Add WebSocket connection limits
4. Implement token bucket or sliding window

---

### BUG #10: No Authentication 🟢

**Priority**: LOW (enhancement)
**Impact**: Anyone on network can access Opcode
**Affects**: Shared network deployments

**Problem**: No authentication mechanism. Anyone with network access can use the server.

**Impact**:
- All projects visible to anyone
- No user isolation
- Inappropriate for multi-user scenarios

**Workaround**: Use VPN or SSH tunnel.

**Fix Difficulty**: HIGH
**Fix Approach**:
1. Add authentication middleware (OAuth, JWT, basic auth)
2. Session management with user context
3. Per-user project isolation
4. Permission system

---

## Desktop vs Web Differences

### Feature Comparison

| Feature | Desktop (Tauri) | Web Server | Notes |
|---------|-----------------|------------|-------|
| Claude Execution | ✅ Full | ✅ Full | Same binary, same args |
| Process Cancellation | ✅ Works | ❌ Broken | BUG #2 |
| stderr Capture | ✅ Yes | ❌ No | BUG #3 |
| Session Isolation | ✅ Yes | ❌ No | BUG #1 |
| Event System | Tauri Events | DOM Events | Different APIs |
| Process Registry | ✅ Yes | ❌ No | Desktop tracks processes |
| Multi-session | ✅ Yes | ❌ No | Web breaks with >1 session |
| Agent Execution | ✅ Yes | ❌ Stub | No DB in web mode |
| Usage Tracking | ✅ Yes | ❌ Stub | No DB in web mode |
| MCP Servers | ✅ Yes | ❌ Stub | No DB in web mode |
| Slash Commands | ✅ Yes | ❌ Stub | No DB in web mode |
| Project Browsing | ✅ Yes | ✅ Yes | Both read ~/.claude |
| Session History | ✅ Yes | ✅ Yes | Both read JSONL files |
| Settings | ✅ Read/Write | ✅ Read-only | Web returns defaults |
| Binary Detection | ✅ Advanced | ⚠️ Basic | BUG #7 |
| Authentication | N/A | ❌ None | BUG #10 |
| CORS | N/A | ⚠️ Permissive | BUG #8 |

### Architecture Differences

**Desktop (Tauri)**:
```
Frontend (React) → Tauri IPC → Rust Commands → Process Registry → Claude Binary
                         ↓
                   Tauri Events → Frontend
```

**Web Server**:
```
Frontend (React) → WebSocket/REST → Axum Handlers → AppState (HashMap) → Claude Binary
                         ↓
                 DOM Events ← WebSocket Messages ← stdout stream
```

**Key Difference**: Desktop has robust process management (`ProcessRegistry`), web server has minimal state (`HashMap<String, Sender>`).

---

## Security Considerations

### Current Security Posture

**INSECURE FOR PUBLIC DEPLOYMENT**

Issues:
1. **No authentication** - Anyone can access
2. **CORS wide open** - Any origin allowed
3. **No rate limiting** - DoS possible
4. **No input validation** - Potential injection
5. **Arbitrary file access** - Can read any ~/.claude file
6. **Process spawning** - Users can spawn unlimited processes
7. **No HTTPS enforcement** - Traffic unencrypted

### Threat Model

**Attack Scenarios**:

1. **Unauthorized Access**: Attacker scans network, finds port 8080, accesses Opcode
2. **Data Exfiltration**: Attacker reads project files, session history, API keys in prompts
3. **Resource Exhaustion**: Attacker spawns many Claude processes, crashes server
4. **CSRF**: Malicious website makes requests to Opcode server on behalf of user
5. **Path Traversal**: Attacker provides malicious `project_path` to read arbitrary files

### Security Best Practices

**For Local Development** (current use case):
- ✅ Bind to localhost only: `127.0.0.1:8080`
- ✅ Use on trusted network only
- ✅ Don't expose to internet
- ⚠️ Close server when not in use

**For Production Deployment** (NOT RECOMMENDED):
```rust
// 1. Add HTTPS/TLS
let tls_config = TlsConfig::from_pem_file("cert.pem", "key.pem")?;

// 2. Add authentication
let auth_layer = tower_http::auth::RequireAuthorizationLayer::bearer("secret-token");

// 3. Restrict CORS
let cors = CorsLayer::new()
    .allow_origin("https://yourdomain.com".parse()?);

// 4. Add rate limiting
let rate_limit = RateLimitLayer::new(100, Duration::from_secs(60));

// 5. Validate inputs
fn validate_project_path(path: &str) -> Result<PathBuf> {
    let canonical = PathBuf::from(path).canonicalize()?;
    if !canonical.starts_with("/Users") {
        return Err("Invalid path".to_string());
    }
    Ok(canonical)
}

// 6. Add audit logging
log::info!("User {} executed: {}", user_id, prompt);
```

### Dangerous Flags

```rust
"--dangerously-skip-permissions" // ← Used in web mode
```

**Risk**: Bypasses Claude Code's built-in permission prompts. User cannot approve/deny tool usage.

**Mitigation**: Remove this flag if deploying publicly, accept that users must approve tools via terminal.

---

## Deployment Guide

### Local Development (Recommended)

**Start Server**:
```bash
cd /Users/max/local/opcode
bun run build           # Build frontend
cargo run --bin opcode-web -- --port 8080
```

**Access**:
- Desktop: `http://localhost:8080`
- Phone (same WiFi): `http://YOUR_PC_IP:8080`

**Find Your IP**:
```bash
# macOS
ipconfig getifaddr en0

# Linux
ip addr show | grep "inet "

# Windows
ipconfig | findstr IPv4
```

### Reverse Proxy (nginx)

**Use Case**: Add HTTPS, authentication, rate limiting

**nginx.conf**:
```nginx
upstream opcode {
    server 127.0.0.1:8080;
}

server {
    listen 443 ssl http2;
    server_name opcode.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=opcode:10m rate=10r/s;
    limit_req zone=opcode burst=20;

    # Basic auth
    auth_basic "Opcode Access";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://opcode;
        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### systemd Service

**opcode-web.service**:
```ini
[Unit]
Description=Opcode Web Server
After=network.target

[Service]
Type=simple
User=opcode
WorkingDirectory=/opt/opcode
ExecStart=/opt/opcode/opcode-web --port 8080
Restart=on-failure
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/opcode/.claude

[Install]
WantedBy=multi-user.target
```

**Install**:
```bash
sudo cp opcode-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable opcode-web
sudo systemctl start opcode-web
sudo systemctl status opcode-web
```

### Docker (Experimental)

**Dockerfile**:
```dockerfile
FROM rust:1.80 as builder

WORKDIR /app
COPY . .
RUN cargo build --release --bin opcode-web

FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code (if bundled)
COPY --from=builder /app/src-tauri/binaries/claude-code-x86_64-unknown-linux-gnu /usr/local/bin/claude
RUN chmod +x /usr/local/bin/claude

# Copy binary
COPY --from=builder /app/target/release/opcode-web /usr/local/bin/

# Create user
RUN useradd -m -u 1000 opcode
USER opcode

# Volume for .claude data
VOLUME /home/opcode/.claude

EXPOSE 8080
CMD ["opcode-web", "--port", "8080", "--host", "0.0.0.0"]
```

**Run**:
```bash
docker build -t opcode-web .
docker run -d \
  -p 8080:8080 \
  -v ~/.claude:/home/opcode/.claude \
  --name opcode \
  opcode-web
```

---

## Performance & Scaling

### Resource Usage

**Per Session**:
- 1 WebSocket connection
- 1 Claude subprocess (~100-500 MB RAM)
- 2 tokio tasks (stdout reader + message forwarder)
- 1 channel (100 message buffer)

**Server Overhead**:
- Axum web server: ~10 MB RAM
- Static file serving: minimal
- HashMap storage: ~1 KB per session

### Bottlenecks

1. **Claude Process Limit**: Each session spawns a Claude process. System process limit applies.
   - Linux default: ~32K processes per user
   - Practical limit: ~10-50 concurrent Claude sessions depending on RAM

2. **Memory**: Each Claude session uses 100-500 MB RAM
   - 8 GB RAM: ~10-15 sessions
   - 16 GB RAM: ~20-30 sessions
   - 32 GB RAM: ~40-60 sessions

3. **WebSocket Connections**: Axum can handle 10K+ connections, but Claude processes are the real limit

4. **Network Bandwidth**: Streaming output uses minimal bandwidth (~10 KB/s per session)

### Scaling Strategies

**Vertical Scaling** (Single Server):
```
Current: 1 server, 1 session at a time (bugs prevent multi-session)
Target: 1 server, 10-50 concurrent sessions (after fixing bugs)
```

**Horizontal Scaling** (Multiple Servers):
- ❌ Not currently possible - no shared state
- Needs: Redis for session storage, message queue for WebSocket distribution
- Complexity: HIGH

**Hybrid Approach**:
- Run multiple `opcode-web` instances on different ports (8080, 8081, 8082...)
- Use nginx load balancer with IP hash (sticky sessions)
- Each instance handles its own processes independently

### Performance Optimizations

1. **Process Pooling** (Future):
   ```rust
   // Keep Claude processes warm, reuse for new sessions
   struct ProcessPool {
       available: VecDeque<Child>,
       max_size: usize,
   }
   ```

2. **Output Buffering**:
   ```rust
   // Buffer multiple lines before sending to reduce WebSocket messages
   let mut buffer = Vec::new();
   while let Ok(Some(line)) = lines.next_line().await {
       buffer.push(line);
       if buffer.len() >= 10 || timeout {
           send_batch(&buffer).await;
           buffer.clear();
       }
   }
   ```

3. **Lazy Session Loading**:
   - Don't load full session history until requested
   - Stream large JSONL files instead of loading into memory

---

## Testing Guide

### Manual Testing Checklist

#### Basic Functionality

- [ ] Server starts successfully: `cargo run --bin opcode-web`
- [ ] Frontend loads at `http://localhost:8080`
- [ ] Can select project directory
- [ ] Can send prompt and receive response
- [ ] Output streams in real-time
- [ ] Session completes without errors

#### Session Management

- [ ] Can view list of projects
- [ ] Can view list of sessions for a project
- [ ] Can load previous session history
- [ ] Can resume existing session

#### Error Handling

- [ ] Invalid project path shows error
- [ ] Claude binary not found shows error
- [ ] WebSocket disconnect recovers gracefully
- [ ] Server restart doesn't corrupt sessions

#### Known Issues to Verify

- [ ] **BUG #1**: Open two tabs → both receive same output (BROKEN)
- [ ] **BUG #2**: Click cancel → process continues (BROKEN)
- [ ] **BUG #3**: Trigger Claude error → error not shown (BROKEN)
- [ ] **BUG #4**: Cancel session → no cancelled event (BROKEN)
- [ ] **BUG #6**: Close tab → process still running (BROKEN)

### Automated Testing (TODO)

**Integration Tests**:
```rust
#[tokio::test]
async fn test_claude_execution_websocket() {
    let app = create_test_app().await;
    let ws = connect_websocket("ws://localhost:8080/ws/claude").await;

    ws.send(json!({
        "command_type": "execute",
        "project_path": "/tmp/test",
        "prompt": "echo hello",
        "model": "sonnet"
    })).await;

    let msg = ws.recv().await;
    assert_eq!(msg["type"], "start");

    // ... more assertions
}
```

**Load Testing**:
```bash
# Using wrk for HTTP endpoints
wrk -t4 -c100 -d30s http://localhost:8080/api/projects

# Using websocat for WebSocket
for i in {1..10}; do
    websocat ws://localhost:8080/ws/claude &
done
```

### Testing Fixes

**After Fixing BUG #1 (Session Isolation)**:
```javascript
// Open two browser tabs
// Tab 1:
const ws1 = new WebSocket('ws://localhost:8080/ws/claude');
ws1.send(JSON.stringify({command_type: 'execute', prompt: 'test1', ...}));

// Tab 2:
const ws2 = new WebSocket('ws://localhost:8080/ws/claude');
ws2.send(JSON.stringify({command_type: 'execute', prompt: 'test2', ...}));

// Listen for events
window.addEventListener('claude-output:session-1', e => console.log('Tab 1:', e.detail));
window.addEventListener('claude-output:session-2', e => console.log('Tab 2:', e.detail));

// Verify: Tab 1 only sees session-1 events, Tab 2 only sees session-2 events
```

**After Fixing BUG #2 (Cancellation)**:
```bash
# Start long-running session
curl -X POST http://localhost:8080/ws/claude \
  -d '{"command_type": "execute", "prompt": "long task", ...}'

# Get session ID from response
SESSION_ID="uuid-here"

# Cancel it
curl http://localhost:8080/api/sessions/$SESSION_ID/cancel

# Verify process killed
ps aux | grep claude | grep $SESSION_ID
# Should return empty (process terminated)
```

---

## Client Examples

### JavaScript/TypeScript WebSocket Client

```typescript
class OpcodeClient {
  private ws: WebSocket | null = null;
  private listeners: Map<string, Function[]> = new Map();

  connect(url: string = 'ws://localhost:8080/ws/claude') {
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('Connected to Opcode');
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.type === 'output') {
        const claudeMessage = JSON.parse(message.content);
        this.emit('output', claudeMessage);
      } else if (message.type === 'completion') {
        this.emit('complete', message.status === 'success');
      } else if (message.type === 'error') {
        this.emit('error', message.message);
      }
    };

    this.ws.onerror = (error) => {
      this.emit('error', error);
    };

    this.ws.onclose = () => {
      this.emit('close', null);
    };
  }

  execute(projectPath: string, prompt: string, model: string = 'claude-3-5-sonnet-20241022') {
    if (!this.ws) throw new Error('Not connected');

    this.ws.send(JSON.stringify({
      command_type: 'execute',
      project_path: projectPath,
      prompt: prompt,
      model: model,
    }));
  }

  continue(projectPath: string, prompt: string, model: string = 'claude-3-5-sonnet-20241022') {
    if (!this.ws) throw new Error('Not connected');

    this.ws.send(JSON.stringify({
      command_type: 'continue',
      project_path: projectPath,
      prompt: prompt,
      model: model,
    }));
  }

  resume(projectPath: string, sessionId: string, prompt: string, model: string = 'claude-3-5-sonnet-20241022') {
    if (!this.ws) throw new Error('Not connected');

    this.ws.send(JSON.stringify({
      command_type: 'resume',
      project_path: projectPath,
      session_id: sessionId,
      prompt: prompt,
      model: model,
    }));
  }

  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  private emit(event: string, data: any) {
    const callbacks = this.listeners.get(event) || [];
    callbacks.forEach(cb => cb(data));
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Usage
const client = new OpcodeClient();
client.connect();

client.on('output', (message) => {
  console.log('Claude says:', message);
});

client.on('complete', (success) => {
  console.log('Session complete:', success);
});

client.on('error', (error) => {
  console.error('Error:', error);
});

client.execute('/path/to/project', 'Add a README file');
```

### Python Client

```python
import asyncio
import websockets
import json

class OpcodeClient:
    def __init__(self, url='ws://localhost:8080/ws/claude'):
        self.url = url
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(self.url)
        print('Connected to Opcode')

    async def execute(self, project_path, prompt, model='claude-3-5-sonnet-20241022'):
        request = {
            'command_type': 'execute',
            'project_path': project_path,
            'prompt': prompt,
            'model': model,
        }
        await self.ws.send(json.dumps(request))

        async for message in self.ws:
            data = json.loads(message)

            if data['type'] == 'start':
                print('Starting execution...')

            elif data['type'] == 'output':
                claude_message = json.loads(data['content'])
                print('Output:', claude_message)

            elif data['type'] == 'completion':
                print('Complete:', data['status'])
                break

            elif data['type'] == 'error':
                print('Error:', data['message'])
                break

    async def disconnect(self):
        if self.ws:
            await self.ws.close()

# Usage
async def main():
    client = OpcodeClient()
    await client.connect()
    await client.execute('/path/to/project', 'Add a hello world function')
    await client.disconnect()

asyncio.run(main())
```

### REST API Client (Python)

```python
import requests

class OpcodeRestClient:
    def __init__(self, base_url='http://localhost:8080'):
        self.base_url = base_url

    def list_projects(self):
        response = requests.get(f'{self.base_url}/api/projects')
        data = response.json()
        if data['success']:
            return data['data']
        else:
            raise Exception(data['error'])

    def get_sessions(self, project_id):
        response = requests.get(f'{self.base_url}/api/projects/{project_id}/sessions')
        data = response.json()
        if data['success']:
            return data['data']
        else:
            raise Exception(data['error'])

    def load_session_history(self, session_id, project_id):
        response = requests.get(
            f'{self.base_url}/api/sessions/{session_id}/history/{project_id}'
        )
        data = response.json()
        if data['success']:
            return data['data']
        else:
            raise Exception(data['error'])

# Usage
client = OpcodeRestClient()
projects = client.list_projects()
for project in projects:
    print(f"Project: {project['path']}")
    sessions = client.get_sessions(project['id'])
    for session in sessions:
        print(f"  Session: {session['id']} - {session.get('first_message', 'No message')}")
```

### cURL Examples

**List Projects**:
```bash
curl http://localhost:8080/api/projects | jq
```

**Get Sessions**:
```bash
PROJECT_ID="-Users-max-local-opcode"
curl "http://localhost:8080/api/projects/$PROJECT_ID/sessions" | jq
```

**Load Session History**:
```bash
SESSION_ID="uuid-here"
PROJECT_ID="-Users-max-local-opcode"
curl "http://localhost:8080/api/sessions/$SESSION_ID/history/$PROJECT_ID" | jq
```

**WebSocket with websocat**:
```bash
# Install: cargo install websocat

# Execute command
echo '{"command_type":"execute","project_path":"/tmp/test","prompt":"hello","model":"sonnet"}' \
  | websocat ws://localhost:8080/ws/claude
```

---

## Appendix

### Full API Endpoint List

```
GET  /                                              Serve index.html
GET  /index.html                                    Serve index.html
GET  /assets/*                                      Serve static assets
GET  /vite.svg                                      Serve vite icon

GET  /api/projects                                  List all projects
GET  /api/projects/{project_id}/sessions           Get project sessions
GET  /api/agents                                    List agents (stub)
GET  /api/usage                                     Get usage stats (stub)
GET  /api/settings/claude                           Get Claude settings
GET  /api/settings/claude/version                   Check Claude version
GET  /api/settings/claude/installations             List Claude installations
GET  /api/settings/system-prompt                    Get system prompt
GET  /api/sessions/new                              Open new session
GET  /api/slash-commands                            List slash commands (stub)
GET  /api/mcp/servers                               List MCP servers (stub)
GET  /api/sessions/{session_id}/history/{project_id}  Load session history
GET  /api/sessions/running                          List running sessions (stub)
GET  /api/sessions/execute                          Execute Claude (stub)
GET  /api/sessions/continue                         Continue Claude (stub)
GET  /api/sessions/resume                           Resume Claude (stub)
GET  /api/sessions/{sessionId}/cancel               Cancel execution (BROKEN)
GET  /api/sessions/{sessionId}/output               Get session output (stub)

WS   /ws/claude                                     WebSocket for Claude execution
```

### Code Statistics

```
File                  Lines  Purpose
----                  -----  -------
web_server.rs           848  Main web server implementation
web_main.rs              39  Binary entry point
apiAdapter.ts           444  Frontend WebSocket client & environment detection
useClaudeMessages.ts    205  Frontend event handling hook
commands/claude.rs     1200+ Desktop Claude command handlers (shared logic)
process/registry.rs     538  Desktop process tracking (not used in web mode)
```

### Environment Variables

```bash
# Logging
RUST_LOG=debug              # Enable debug logging
RUST_LOG=trace              # Enable trace logging (very verbose)

# Server configuration
HOST=0.0.0.0               # Bind to all interfaces
PORT=8080                  # Server port

# Claude binary
CLAUDE_PATH=/path/to/claude  # Override Claude binary location
```

### Useful Commands

```bash
# Development
cargo run --bin opcode-web -- --port 8080

# Production build
cargo build --release --bin opcode-web
./target/release/opcode-web

# Check for running processes
ps aux | grep opcode-web

# Kill all Claude processes (DANGER)
pkill claude

# Monitor WebSocket connections
ss -tn | grep :8080

# Test WebSocket upgrade
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: test" \
  -H "Sec-WebSocket-Version: 13" \
  http://localhost:8080/ws/claude
```

---

## Summary

### What Works

1. ✅ Basic Claude execution (single session)
2. ✅ Project and session browsing
3. ✅ Session history loading
4. ✅ WebSocket streaming output
5. ✅ DOM event system
6. ✅ CORS for phone access
7. ✅ Static file serving

### What's Broken

1. ❌ **Multi-session isolation** (BUG #1) - CRITICAL
2. ❌ **Process cancellation** (BUG #2) - CRITICAL
3. ❌ **stderr capture** (BUG #3) - HIGH
4. ❌ **claude-cancelled events** (BUG #4) - MEDIUM
5. ❌ **Process cleanup on disconnect** (BUG #6) - CRITICAL

### Recommended Next Steps

**Priority 1** (Make it usable):
1. Fix BUG #2: Implement process cancellation
2. Fix BUG #6: Clean up processes on disconnect
3. Fix BUG #3: Capture and display stderr

**Priority 2** (Make it production-ready):
4. Fix BUG #1: Implement session-scoped events
5. Add authentication
6. Add rate limiting
7. Fix BUG #8: Restrict CORS

**Priority 3** (Nice to have):
8. Fix remaining bugs (#4, #5, #7, #9, #10)
9. Add database support for agents/usage/MCP
10. Add automated tests

### Current Recommendation

**For Development**: ✅ OK to use (single session only)
**For Production**: ❌ NOT READY (critical bugs, no security)

The web server successfully bridges the gap between desktop and browser access, but requires significant work before it can handle multiple concurrent users or be deployed publicly.
