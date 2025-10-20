# Opcode - Comprehensive Architecture Reference

This document provides a complete architectural overview of Opcode, a desktop GUI wrapper for Claude Code CLI built with React and Tauri.

---

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [System Components](#system-components)
3. [Frontend Architecture](#frontend-architecture)
4. [Backend Architecture](#backend-architecture)
5. [Data Flow & Communication](#data-flow--communication)
6. [State Management](#state-management)
7. [Process Management](#process-management)
8. [Storage & Persistence](#storage--persistence)
9. [Checkpoint & Timeline System](#checkpoint--timeline-system)
10. [Event System](#event-system)
11. [Multi-Platform Support](#multi-platform-support)
12. [Security Boundaries](#security-boundaries)
13. [Design Patterns](#design-patterns)
14. [Extension Points](#extension-points)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                    (React + TypeScript)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Tab Manager  │  │  Components  │  │  Providers   │          │
│  │              │  │              │  │              │          │
│  │ - Tabs       │  │ - Sessions   │  │ - Theme      │          │
│  │ - Navigation │  │ - Agents     │  │ - Tabs       │          │
│  │ - Keyboard   │  │ - Settings   │  │ - Analytics  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ IPC / WebSocket
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      TAURI BACKEND                               │
│                      (Rust + Tokio)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Commands   │  │   Process    │  │  Checkpoint  │          │
│  │              │  │   Registry   │  │   Manager    │          │
│  │ - Claude     │  │              │  │              │          │
│  │ - Agents     │  │ - Tracking   │  │ - Snapshots  │          │
│  │ - MCP        │  │ - Lifecycle  │  │ - Timeline   │          │
│  │ - Storage    │  │ - Streaming  │  │ - Restore    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ Subprocess Management
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                   EXTERNAL PROCESSES                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Claude Code  │  │    Agents    │  │ MCP Servers  │          │
│  │     CLI      │  │   (claude)   │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ File System
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                        DATA LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ ~/.claude/   │  │   SQLite     │  │  LocalStorage│          │
│  │   projects/  │  │   Database   │  │              │          │
│  │   sessions/  │  │              │  │  - Settings  │          │
│  │ checkpoints/ │  │  - Agents    │  │  - Tabs      │          │
│  │              │  │  - Runs      │  │  - Sessions  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

**Unusual Tauri Workflow**:
- Frontend must be built FIRST before running Tauri
- `beforeDevCommand` in tauri.conf.json is intentionally empty
- This is NOT a hot-reload setup - you build once, then run
- **Rationale**: Simplifies build process and ensures consistent deployment across desktop and web modes

**Multiple Binary Strategy**:
- `opcode` (main desktop app) - runs the Tauri GUI
- `opcode-web` (web server) - runs a web server for mobile/browser access
- Uses `default-run = "opcode"` in Cargo.toml to disambiguate

---

## System Components

### 1. Frontend Layer (React + TypeScript)

```
src/
├── components/           # UI Components
│   ├── ClaudeCodeSession.tsx       # Main session interface
│   ├── TabManager.tsx              # Tab management UI
│   ├── AgentExecution.tsx          # Agent running UI
│   ├── Settings.tsx                # Settings panel
│   ├── MCPManager.tsx              # MCP server management
│   ├── UsageDashboard.tsx          # Token usage analytics
│   ├── TimelineNavigator.tsx       # Checkpoint timeline UI
│   └── ui/                         # shadcn/ui components
│
├── contexts/            # React Context Providers
│   ├── TabContext.tsx              # Tab state management
│   └── ThemeContext.tsx            # Theme provider
│
├── hooks/               # Custom React Hooks
│   ├── useTabState.ts              # Tab operations
│   ├── useAnalytics.ts             # Analytics tracking
│   ├── useDebounce.ts              # Debouncing utility
│   └── useApiCall.ts               # API call wrapper
│
├── lib/                 # Utilities & API
│   ├── api.ts                      # Tauri command wrappers
│   ├── apiAdapter.ts               # Tauri/Web compatibility
│   ├── analytics/                  # PostHog integration
│   └── outputCache.tsx             # Session output caching
│
└── services/            # Business Logic
    ├── sessionPersistence.ts       # Session save/restore
    └── tabPersistence.ts           # Tab save/restore
```

### 2. Backend Layer (Rust + Tauri)

```
src-tauri/src/
├── commands/            # Tauri Command Handlers
│   ├── agents.rs                   # Agent CRUD + execution
│   ├── claude.rs                   # Claude CLI integration
│   ├── mcp.rs                      # MCP server management
│   ├── storage.rs                  # SQLite operations
│   ├── usage.rs                    # Token usage analytics
│   ├── slash_commands.rs           # Custom slash commands
│   └── proxy.rs                    # HTTP proxy settings
│
├── checkpoint/          # Checkpoint System
│   ├── manager.rs                  # Checkpoint operations
│   ├── storage.rs                  # File snapshots
│   └── state.rs                    # Global checkpoint state
│
├── process/             # Process Management
│   ├── registry.rs                 # Process tracking
│   └── mod.rs                      # Process utilities
│
├── claude_binary.rs     # Claude installation detection
├── web_server.rs        # Web server for mobile access
├── main.rs              # Desktop app entry point
└── web_main.rs          # Web server entry point
```

---

## Frontend Architecture

### Component Hierarchy

```
App (Root)
├── ThemeProvider
│   └── OutputCacheProvider
│       └── TabProvider
│           ├── CustomTitlebar (macOS custom window controls)
│           └── AppContent
│               ├── TabManager
│               │   └── TabItem[] (draggable, reorderable)
│               └── TabContent (renders active tab)
│                   ├── ClaudeCodeSession (chat tab)
│                   │   ├── SessionHeader
│                   │   ├── MessageList (virtualized)
│                   │   ├── FloatingPromptInput
│                   │   ├── TimelineNavigator
│                   │   └── CheckpointSettings
│                   ├── AgentExecution (agent run tab)
│                   ├── CCAgents (agents list tab)
│                   ├── Settings (settings tab)
│                   ├── UsageDashboard (usage tab)
│                   └── MCPManager (MCP tab)
```

### State Management Architecture

**Tab State** (TabContext.tsx):
- Centralized tab management with React Context
- Supports up to 20 concurrent tabs (MAX_TABS)
- Persists to localStorage on changes (debounced 500ms)
- Tab types: chat, agent, agents, projects, usage, mcp, settings, claude-md, claude-file

**Session State** (SessionPersistence):
- Saves active Claude sessions to localStorage
- Restores sessions on app restart
- Stores: sessionId, projectPath, messages, checkpoints

**Theme State** (ThemeContext):
- Persists theme preference to SQLite
- Syncs to localStorage for instant load on startup
- Supports: light, dark, system

**Output Cache** (OutputCacheProvider):
- Caches Claude output in memory for performance
- Prevents unnecessary re-parsing of JSONL
- Uses Map<sessionId, messages[]>

### Routing System

Opcode uses a **tab-based navigation** system instead of traditional routing:

- No react-router - tabs act as virtual pages
- Each tab type renders different content via `TabContent.tsx`
- Navigation via keyboard shortcuts:
  - `Cmd/Ctrl+T`: New tab
  - `Cmd/Ctrl+W`: Close tab
  - `Cmd/Ctrl+Tab`: Next tab
  - `Cmd/Ctrl+Shift+Tab`: Previous tab
  - `Cmd/Ctrl+1-9`: Jump to tab by index

---

## Backend Architecture

### Command Pattern

All Tauri commands follow this pattern:

```rust
#[tauri::command]
async fn command_name(
    param: Type,
    state: State<'_, StateType>,
) -> Result<ReturnType, String> {
    // Command logic
    Ok(result)
}
```

Registered in `main.rs`:
```rust
.invoke_handler(tauri::generate_handler![
    command_name,
    // ... other commands
])
```

### State Management (Tauri)

**Managed State**:
- `AgentDb`: SQLite connection for agents database
- `CheckpointState`: Global checkpoint managers by session
- `ProcessRegistryState`: Tracks running Claude/Agent processes
- `ClaudeProcessState`: Manages Claude CLI subprocesses

**State Lifecycle**:
1. Initialized in `.setup()` hook
2. Shared across all command invocations
3. Thread-safe via `Arc<Mutex<T>>`
4. Cleaned up on app shutdown

### Module Organization

**commands/**: Pure functions that handle IPC requests
**checkpoint/**: Stateful checkpoint system with async operations
**process/**: Process lifecycle management and tracking
**claude_binary.rs**: Platform-specific Claude installation detection
**web_server.rs**: Axum-based REST API + WebSocket server

---

## Data Flow & Communication

### Desktop Mode (Tauri IPC)

```
Frontend                    Backend                   External Process
   │                          │                             │
   │──── invoke(command) ────>│                             │
   │                          │──── spawn(claude) ─────────>│
   │                          │                             │
   │<── event(claude-output)──│<──── stdout ────────────────│
   │                          │                             │
   │──── invoke(cancel) ─────>│                             │
   │                          │──── kill() ────────────────>│
   │<── event(claude-complete)│                             │
```

**IPC Commands**:
- Synchronous: Most commands (list_projects, get_agent, etc.)
- Asynchronous with events: execute_claude_code, execute_agent
- Event-based: claude-output, claude-complete, claude-error

### Web Mode (REST + WebSocket)

```
Frontend                  Web Server                  External Process
   │                          │                             │
   │──── GET /api/projects ──>│                             │
   │<─── JSON response ────────│                             │
   │                          │                             │
   │──── WebSocket /ws/claude >│                             │
   │                          │──── spawn(claude) ─────────>│
   │<── {type:"output"} ───────│<──── stdout ────────────────│
   │<── {type:"completion"} ───│                             │
```

**REST Endpoints**: Defined in `web_server.rs`
- `/api/projects` - List projects
- `/api/agents` - Agent operations
- `/api/usage` - Token usage stats
- `/ws/claude` - WebSocket for Claude execution streaming

**API Adapter**: `apiAdapter.ts` provides unified interface
- Detects Tauri vs Web environment
- Routes calls to `invoke()` or `fetch()`
- Simulates Tauri events for web mode via DOM events

---

## State Management

### Frontend State

**1. Component-Level State** (useState)
- Local UI state: loading, errors, form inputs
- Transient state that doesn't need persistence

**2. Context State** (React Context)
- **TabContext**: Global tab management
- **ThemeContext**: Application theme
- **OutputCacheProvider**: Session output caching

**3. Persistent State** (localStorage + SQLite)
- **Tab Persistence**: Active tabs, order, metadata
- **Session Persistence**: Claude sessions, messages, checkpoints
- **Settings**: Theme, startup preferences, proxy config

### Backend State

**1. Managed State** (Tauri State)
```rust
// In main.rs setup()
app.manage(AgentDb(Mutex::new(conn)));
app.manage(CheckpointState::new());
app.manage(ProcessRegistryState::default());
app.manage(ClaudeProcessState::default());
```

**2. Checkpoint State** (CheckpointState)
- HashMap<sessionId, CheckpointManager>
- Manages file snapshots and timeline trees
- Async operations with RwLock

**3. Process Registry** (ProcessRegistryState)
- Tracks running Claude/Agent processes
- HashMap<runId, ProcessHandle>
- Monitors PIDs and stdout streams

---

## Process Management

### Process Registry Architecture

```rust
pub struct ProcessRegistry {
    processes: Arc<Mutex<HashMap<i64, ProcessHandle>>>,
    next_id: Arc<Mutex<i64>>,
}

pub struct ProcessHandle {
    pub info: ProcessInfo,
    pub child: Arc<Mutex<Option<Child>>>,
    pub live_output: Arc<Mutex<String>>,
}

pub enum ProcessType {
    AgentRun { agent_id: i64, agent_name: String },
    ClaudeSession { session_id: String },
}
```

**Process Lifecycle**:
1. **Register**: `register_process(run_id, agent_id, pid, ...)`
2. **Track**: Store ProcessHandle with child process
3. **Stream**: Capture stdout via tokio::process
4. **Monitor**: Check process status with `try_wait()`
5. **Kill**: Graceful SIGTERM → wait 2s → SIGKILL
6. **Cleanup**: Remove from registry on exit

### Process Killing Strategy

```rust
// 1. Send SIGTERM for graceful shutdown
child.start_kill();

// 2. Wait up to 5 seconds
tokio::time::timeout(Duration::from_secs(5), wait_for_exit()).await;

// 3. Fallback: system kill command
if cfg!(target_os = "windows") {
    taskkill /F /PID {pid}
} else {
    kill -TERM {pid}  // then kill -KILL if needed
}

// 4. Cleanup: remove from registry
unregister_process(run_id)
```

**Why this matters**: Claude processes can leave background tasks running if not terminated properly. The multi-stage kill ensures clean shutdown.

---

## Storage & Persistence

### SQLite Database Schema

**Location**: `~/.claude/opcode.db`

```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    icon TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    default_task TEXT,
    model TEXT NOT NULL DEFAULT 'sonnet',
    hooks TEXT,  -- JSON: HooksConfiguration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    agent_name TEXT NOT NULL,
    agent_icon TEXT NOT NULL,
    task TEXT NOT NULL,
    model TEXT NOT NULL,
    project_path TEXT NOT NULL,
    session_id TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'pending', 'running', 'completed', 'failed', 'cancelled'
    pid INTEGER,
    process_started_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

CREATE TABLE app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

**Indexing**:
- agent_runs: indexed on `(agent_id, created_at DESC)`
- agent_runs: indexed on `session_id` for history lookups

### File System Structure

```
~/.claude/
├── opcode.db                    # SQLite database
├── settings.json                # Claude Code settings
├── CLAUDE.md                    # Global system prompt
├── projects/
│   └── {encoded_project_path}/  # One directory per project
│       ├── sessions/
│       │   └── {session_uuid}.jsonl    # Session messages
│       └── checkpoints/
│           └── {session_uuid}/
│               ├── timeline.json
│               ├── {checkpoint_id}/
│               │   ├── checkpoint.json
│               │   ├── messages.jsonl
│               │   └── snapshots/
│               │       ├── file1.json
│               │       └── file2.json
│               └── ...
```

### LocalStorage (Browser)

**Keys**:
- `opcode_tabs_v2`: Serialized tab state
- `opcode_active_tab`: Active tab ID
- `opcode_sessions_{sessionId}`: Session restore data
- `app_setting:{key}`: Mirrored SQLite settings for instant load

---

## Checkpoint & Timeline System

### Architecture

**Design Goal**: Git-like version control for Claude sessions with file snapshots

```
SessionTimeline
└── rootNode (TimelineNode)
    ├── checkpoint: Checkpoint
    ├── children: [TimelineNode, ...]
    └── fileSnapshotIds: [String, ...]
```

### Checkpoint Structure

```rust
pub struct Checkpoint {
    pub id: String,                      // UUID
    pub session_id: String,
    pub project_id: String,
    pub message_index: usize,            // Position in JSONL
    pub timestamp: DateTime<Utc>,
    pub description: Option<String>,
    pub parent_checkpoint_id: Option<String>,
    pub metadata: CheckpointMetadata,
}

pub struct CheckpointMetadata {
    pub total_tokens: u64,
    pub model_used: String,
    pub user_prompt: String,
    pub file_changes: usize,
    pub snapshot_size: u64,
}

pub struct FileSnapshot {
    pub checkpoint_id: String,
    pub file_path: PathBuf,
    pub content: String,
    pub hash: String,                    // SHA-256
    pub is_deleted: bool,
    pub permissions: Option<u32>,        // Unix permissions
    pub size: u64,
}
```

### Checkpoint Strategies

**Manual**: User explicitly creates checkpoints
**PerPrompt**: Checkpoint after every user message
**PerToolUse**: Checkpoint after any tool usage
**Smart**: Checkpoint after destructive tools (write, edit, bash, rm)

### File Tracking

**Intelligent Tracking**:
1. Watch tool_use events in Claude messages
2. Extract file paths from Edit, Write, MultiEdit tools
3. Track bash commands for side effects
4. Compare file hashes before/after operations
5. Only snapshot files that actually changed

**Tracked State**:
```rust
pub struct FileState {
    pub last_hash: String,
    pub is_modified: bool,
    pub last_modified: DateTime<Utc>,
    pub exists: bool,
}
```

### Restore Process

**Checkpoint Restoration**:
1. Load checkpoint data from `checkpoints/{session}/{checkpoint_id}/`
2. Scan entire project directory for current files
3. Delete files not in checkpoint
4. Restore files from snapshots
5. Update file tracker with restored state
6. Reload JSONL messages
7. Update timeline current_checkpoint_id

**Key Innovation**: Full project restoration, not just changed files. This ensures complete state consistency.

---

## Event System

### Desktop Mode (Tauri Events)

**Event Flow**:
```rust
// Backend emits
window.emit("claude-output", message)?;

// Frontend listens
const unlisten = await listen("claude-output", (event) => {
    handleMessage(event.payload);
});
```

**Events**:
- `claude-output`: JSONL message from Claude
- `claude-complete`: Session finished
- `claude-error`: Error occurred
- `claude-cancelled`: User cancelled
- `claude-not-found`: Claude binary not detected

### Web Mode (DOM Events)

**Polyfill Strategy**:
```typescript
// apiAdapter.ts creates DOM event simulation
window.dispatchEvent(new CustomEvent('claude-output', {
    detail: message
}));

// Components listen the same way
window.addEventListener('claude-output', handler);
```

**Why this works**: Provides consistent API between Tauri and web modes. Frontend code doesn't need to know which environment it's in.

---

## Multi-Platform Support

### Desktop (Tauri)

**Supported Platforms**:
- macOS (aarch64-apple-darwin, x86_64-apple-darwin)
- Linux (x86_64-unknown-linux-gnu)
- Windows (x86_64-pc-windows-msvc)

**Platform-Specific Features**:
- **macOS**: Window vibrancy, custom titlebar, NSVisualEffectMaterial
- **Linux**: Standard window decorations
- **Windows**: Standard window decorations

### Web Server Mode

**Purpose**: Access Opcode from mobile devices or remote browsers

**Launch**:
```bash
cargo run --bin opcode-web -- --port 8080
```

**Architecture**:
- Axum web server with CORS enabled
- REST API for command invocations
- WebSocket for streaming Claude output
- Serves pre-built React frontend from `dist/`

**Critical Limitations** (documented in web_server.design.md):
1. Session-scoped events are BROKEN (global, not per-session)
2. Process cancellation NOT IMPLEMENTED
3. stderr not captured
4. Only single user, single session supported

### API Adapter Pattern

**Environment Detection**:
```typescript
function detectEnvironment(): boolean {
    return !!(
        window.__TAURI__ ||
        window.__TAURI_METADATA__ ||
        navigator.userAgent.includes('Tauri')
    );
}
```

**Unified API**:
```typescript
export async function apiCall<T>(command: string, params?: any): Promise<T> {
    const isTauri = detectEnvironment();

    if (isTauri) {
        return await invoke<T>(command, params);
    } else {
        const endpoint = mapCommandToEndpoint(command);
        return await restApiCall<T>(endpoint, params);
    }
}
```

---

## Security Boundaries

### Trust Boundaries

```
1. User Input
   ↓ (Validation in UI)
2. Frontend State
   ↓ (Tauri IPC)
3. Rust Command Handlers
   ↓ (Command execution)
4. External Processes (Claude, Agents)
   ↓ (File system access)
5. User's Project Files
```

### Security Measures

**1. Subprocess Sandboxing**:
- Claude processes run with user's permissions
- No privilege escalation
- Process isolation via tokio::process

**2. File System Access**:
- Claude only accesses project directory
- No system file access
- Checkpoints stored in `~/.claude/` (user-controlled)

**3. API Key Security**:
- Keys stored in `~/.claude/settings.json`
- Never exposed to frontend
- Not logged or transmitted

**4. SQLite Injection Prevention**:
```rust
// Always use parameterized queries
conn.execute(
    "INSERT INTO agents (name) VALUES (?1)",
    params![&name],
)?;
```

**5. WebSocket Authentication**:
- Web mode has NO authentication
- Should only be used on trusted local networks
- NOT production-ready for public internet

---

## Design Patterns

### 1. Command Pattern (Tauri)

All backend operations use command pattern:
```rust
#[tauri::command]
async fn operation_name(state: State<'_, AppState>) -> Result<T, String>
```

**Benefits**:
- Testable in isolation
- Consistent error handling
- Easy to add logging/metrics

### 2. Repository Pattern (Storage)

SQLite access wrapped in repository-like functions:
```rust
pub fn get_agent(conn: &Connection, id: i64) -> Result<Agent, rusqlite::Error>
pub fn create_agent(conn: &Connection, agent: NewAgent) -> Result<Agent, rusqlite::Error>
```

**Benefits**:
- Centralized database logic
- Reusable across commands
- Easy to mock for testing

### 3. Observer Pattern (Events)

Event-driven architecture for async operations:
```typescript
listen('claude-output', handleMessage);
emit('claude-output', message);
```

**Benefits**:
- Decoupled components
- Real-time UI updates
- Easy to add listeners

### 4. Strategy Pattern (Checkpoints)

Checkpoint strategy is configurable:
```rust
pub enum CheckpointStrategy {
    Manual,
    PerPrompt,
    PerToolUse,
    Smart,
}
```

**Benefits**:
- User-configurable behavior
- Easy to add new strategies
- Testable in isolation

### 5. Adapter Pattern (API)

API adapter abstracts Tauri vs Web:
```typescript
apiCall('list_projects') // Works in both modes
```

**Benefits**:
- Platform-agnostic frontend
- Easy to test
- Graceful degradation

### 6. Provider Pattern (React)

Context providers for global state:
```tsx
<ThemeProvider>
  <TabProvider>
    <AppContent />
  </TabProvider>
</ThemeProvider>
```

**Benefits**:
- Avoids prop drilling
- Composable context
- Easy to add providers

### 7. Singleton Pattern (System Tabs)

Certain tabs are singletons (Settings, Usage, MCP):
```typescript
const existingTab = tabs.find(tab => tab.type === 'settings');
if (existingTab) {
    setActiveTab(existingTab.id);
    return existingTab.id;
}
```

**Benefits**:
- Prevents duplicate system UI
- Consistent UX
- State preservation

---

## Extension Points

### 1. Adding New Tab Types

**Steps**:
1. Add type to `Tab` interface in `TabContext.tsx`:
   ```typescript
   type: 'chat' | 'agent' | 'my-new-type'
   ```
2. Create component in `components/MyNewTab.tsx`
3. Add rendering case in `TabContent.tsx`:
   ```typescript
   case 'my-new-type':
     return <MyNewTab />;
   ```
4. Add creator function in `useTabState.ts`:
   ```typescript
   const createMyNewTab = useCallback(() => {
     return addTab({ type: 'my-new-type', ... });
   }, [addTab]);
   ```

### 2. Adding New Tauri Commands

**Steps**:
1. Define command in `src-tauri/src/commands/my_module.rs`:
   ```rust
   #[tauri::command]
   pub async fn my_command(param: String) -> Result<String, String> {
       Ok(format!("Processed: {}", param))
   }
   ```
2. Register in `main.rs`:
   ```rust
   .invoke_handler(tauri::generate_handler![
       my_command,
   ])
   ```
3. Add TypeScript wrapper in `src/lib/api.ts`:
   ```typescript
   async myCommand(param: string): Promise<string> {
       return await apiCall<string>("my_command", { param });
   }
   ```
4. Add REST endpoint in `web_server.rs` (for web mode):
   ```rust
   async fn my_command(Path(param): Path<String>) -> Json<ApiResponse<String>> {
       // Implementation
   }
   ```

### 3. Adding New Checkpoint Strategies

**Steps**:
1. Add variant to `CheckpointStrategy` enum:
   ```rust
   pub enum CheckpointStrategy {
       Manual,
       PerPrompt,
       PerToolUse,
       Smart,
       MyStrategy,
   }
   ```
2. Implement logic in `checkpoint/manager.rs`:
   ```rust
   CheckpointStrategy::MyStrategy => {
       // Custom trigger logic
   }
   ```

### 4. Adding New Agent Capabilities

**Steps**:
1. Extend `agents` table schema with new columns
2. Update `Agent` struct in `commands/agents.rs`
3. Add UI controls in `CreateAgent.tsx`
4. Update `execute_agent` to use new capabilities

### 5. Adding New Analytics Events

**Steps**:
1. Define event in `src/lib/analytics/events.ts`:
   ```typescript
   export const trackMyEvent = (data: MyEventData) => {
       analytics.track('my_event', data);
   };
   ```
2. Use in components:
   ```typescript
   const trackEvent = useTrackEvent();
   trackEvent.myEvent({ ... });
   ```

---

## Why the Unusual Tauri Workflow?

**Traditional Tauri Setup**:
```json
"beforeDevCommand": "npm run dev",
"beforeBuildCommand": "npm run build"
```
- Vite dev server runs during development
- Hot module replacement
- Fast iteration

**Opcode's Setup**:
```json
"beforeDevCommand": "",
"beforeBuildCommand": "bun run build"
```
- Frontend must be built first
- No HMR during Tauri dev
- Requires manual rebuild for frontend changes

### Rationale

**1. Dual-Mode Support**:
- Same build artifacts work for desktop AND web server
- Ensures consistency across deployment modes
- No conditional compilation needed

**2. Simplified Deployment**:
- One build step produces both modes
- No separate bundling logic
- dist/ folder is always ready to serve

**3. Deterministic Builds**:
- No race conditions between Vite dev server and Tauri
- Predictable build output
- Easier to debug

**4. Web Server Architecture**:
- Web mode serves pre-built static files
- No need for separate Vite instance
- Lighter resource footprint

**Trade-offs**:
- Slower development iteration (need to rebuild)
- No HMR for frontend changes
- Mitigated by: fast Bun builds (~3-4s)

---

## Conclusion

Opcode's architecture balances several competing concerns:

1. **Developer Experience**: Fast iteration with Bun, hot-reload for Rust
2. **User Experience**: Responsive UI with virtualized lists, optimistic updates
3. **Reliability**: Process management, error recovery, checkpoint system
4. **Portability**: Desktop (3 platforms) + Web server mode
5. **Maintainability**: Clear separation of concerns, consistent patterns

The unusual build workflow and dual-binary approach enable running on desktop AND mobile while maintaining a single codebase. The checkpoint system provides Git-like versioning for AI interactions, and the process registry ensures robust subprocess management.

For agents exploring this codebase: This document should provide everything needed to understand the system architecture, add features, debug issues, and make informed design decisions.
