# Lessons Learned - Opcode Development Wisdom

This document captures hard-earned wisdom, best practices, and anti-patterns discovered during the development of Opcode. These lessons should guide future development and help new contributors avoid common pitfalls.

## Table of Contents

- [Core Philosophy](#core-philosophy)
- [Architecture Lessons](#architecture-lessons)
- [Tauri-Specific Lessons](#tauri-specific-lessons)
- [React/Frontend Lessons](#react-frontend-lessons)
- [Rust/Backend Lessons](#rust-backend-lessons)
- [Build System Lessons](#build-system-lessons)
- [Process Management Lessons](#process-management-lessons)
- [Testing Lessons](#testing-lessons)
- [Performance Lessons](#performance-lessons)
- [Security Lessons](#security-lessons)
- [Developer Experience Lessons](#developer-experience-lessons)
- [Debugging Wisdom](#debugging-wisdom)
- [Refactoring Lessons](#refactoring-lessons)
- [Technical Debt Lessons](#technical-debt-lessons)
- [Do's and Don'ts](#dos-and-donts)
- [External Resources](#external-resources)
- [Future Recommendations](#future-recommendations)

---

## Core Philosophy

### 1. **Always research before editing**
Web search revealed the right solution for the multiple binaries issue. Don't assume you know the answer - check documentation, GitHub issues, Stack Overflow, and official sources first.

**Example**: When facing the "multiple binaries" Cargo error, researching led to the correct solution (`default-run = "opcode"` in Cargo.toml) instead of trying to modify Tauri's configuration in unsupported ways.

### 2. **Test manually first**
Confirmed the approach before permanent changes. Always validate fixes in development before committing.

**Example**: Tested `bun run tauri dev -- --bin opcode` manually to verify the approach worked before editing Cargo.toml.

### 3. **Read the justfile**
It documents the intended workflow. Build automation files are documentation too - they tell you how the project is meant to be built and run.

**Why this matters**: The justfile clearly showed the build-first workflow (`build-frontend` then `cargo run`), preventing assumptions about hot-reload development.

### 4. **Documentation is code**
Comprehensive documentation in CLAUDE.md prevented repeated mistakes and helped new developers understand non-standard workflows quickly.

---

## Architecture Lessons

### Multi-Binary Architecture

**Decision**: Two separate binaries (`opcode` for desktop, `opcode-web` for web server) in one codebase.

**Why it works**:
- Shared business logic via `lib.rs`
- Different entry points for different deployment modes
- Single codebase, multiple deployment targets

**Key learning**: Set `default-run = "opcode"` in `[package]` section to specify which binary to use by default.

### Build-First, Not Hot-Reload

**This is NOT typical Tauri**: Frontend must be built FIRST before running Tauri.

**The workflow**:
1. `bun run build` - Build frontend to `dist/`
2. `bun run tauri dev` - Run desktop app
3. Make changes → rebuild → app reloads

**Why**:
- Intentional design choice for this project
- `beforeDevCommand` is intentionally empty in tauri.conf.json
- Simplifies build process for multiple binaries

**Anti-pattern**: Don't try to enable hot-reload by modifying Tauri config - it will break the web server binary.

### Dual Environment Support (Tauri + Web)

**Pattern**: `apiAdapter.ts` provides unified interface for both environments.

**Key components**:
- Environment detection via `window.__TAURI__` checks
- REST API fallback for web browsers
- WebSocket streaming for real-time updates
- DOM events to simulate Tauri events in web mode

**Best practice**: Always design commands to work in both environments from day one, even if you're only building for desktop initially.

**Critical insight**: Session-scoped events (`claude-output:${sessionId}`) are essential for multi-session support but easy to forget in web mode.

### Component Modularization

**Success story**: ClaudeCodeSession refactored from 1000+ lines into:
- `useClaudeMessages.ts` - Message handling logic
- `useCheckpoints.ts` - Checkpoint management
- `MessageList.tsx` - Message rendering
- `PromptQueue.tsx` - Queue management
- `SessionHeader.tsx` - Header UI

**Benefits**:
- Easier testing
- Better separation of concerns
- Reusable hooks
- More maintainable code

**Lesson**: Start with extraction into hooks, then extract UI components. Logic first, then presentation.

---

## Tauri-Specific Lessons

### 1. **Tauri 2 Configuration Schema is Strict**

**What NOT to do**:
```json
// ❌ This doesn't work - Tauri 2 doesn't support this
"build": {
  "runner": {
    "args": ["--bin", "opcode"]
  }
}
```

**Why**: Tauri 2's `runner` field only accepts a string (binary name), not an object with arguments.

**The right way**: Use Cargo's standard `default-run` configuration.

### 2. **Sidecar Binaries Are Not Worth It**

**Major refactor** (commit `4ddb6a1`): Removed all bundled/sidecar binary support.

**Why removed**:
- Added 1,500+ lines of complex build code
- Required platform-specific scripts
- Difficult to maintain and debug
- System-installed binaries are more reliable
- Users typically have Claude installed anyway

**Lesson**: Don't bundle binaries unless absolutely necessary. System detection is simpler and more maintainable.

### 3. **Process Environment Inheritance**

**Critical pattern** in `claude_binary.rs`:
```rust
pub fn create_command_with_env(program: &str) -> Command {
    let mut cmd = Command::new(program);

    // Inherit essential environment variables
    for (key, value) in std::env::vars() {
        if key == "PATH" || key == "HOME" || key == "NVM_BIN" || ... {
            cmd.env(&key, &value);
        }
    }
}
```

**Why essential**: Tauri apps don't inherit full shell environment. Must explicitly pass PATH, NVM_BIN, HOMEBREW_PREFIX, etc.

**Gotcha**: NVM installations won't work without `NVM_BIN` environment variable.

### 4. **Platform-Specific Binary Detection**

**Pattern**: Support multiple discovery methods:
1. `which` command (Unix) / `where` command (Windows)
2. NVM directories check
3. Standard paths (`/usr/local/bin`, Homebrew, etc.)
4. User-specific paths (`~/.local/bin`, `~/bin`)

**Key insight**: In production builds, version detection may fail due to process spawning restrictions. The binary's mere existence is enough - version is nice-to-have.

**Windows gotcha**: Must check for `.exe` and `.cmd` extensions.

### 5. **Tauri Events vs DOM Events**

**Pattern for web compatibility**:
```typescript
const listen = tauriListen || ((eventName: string, callback: (event: any) => void) => {
  const domEventHandler = (event: any) => {
    callback({ payload: event.detail });
  };
  window.addEventListener(eventName, domEventHandler);
  return Promise.resolve(() => window.removeEventListener(eventName, domEventHandler));
});
```

**Why**: Allows same code to work in both Tauri desktop and web browser environments.

---

## React/Frontend Lessons

### 1. **State Management: Context + Zustand Hybrid**

**Pattern used**:
- Context API for theme and tab management
- Zustand for complex state (future implementation)
- Local state for UI-only concerns

**When to use what**:
- **Context**: Cross-cutting concerns (theme, auth, global settings)
- **Zustand**: Complex state with selectors and performance needs
- **Local state**: Component-specific, not shared

**Anti-pattern**: Don't lift all state to context - causes unnecessary re-renders.

### 2. **Custom Hooks for Logic Extraction**

**Excellent examples**:
- `useApiCall.ts` - API call management with loading/error states
- `useDebounce.ts` - Debounced values
- `usePagination.ts` - Pagination logic
- `usePerformanceMonitor.ts` - Performance tracking

**Pattern**:
```typescript
export function useApiCall<T>() {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null
  });

  const execute = useCallback(async (fn: () => Promise<T>) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const data = await fn();
      setState({ data, loading: false, error: null });
    } catch (error) {
      setState({ data: null, loading: false, error });
    }
  }, []);

  return { ...state, execute };
}
```

**Lesson**: Extract reusable logic into hooks early. Don't wait until you need it in multiple places.

### 3. **Component File Organization**

**Best practice**:
```
components/
├── ClaudeCodeSession.tsx          # Main component
├── ClaudeCodeSession.refactored.tsx  # Keep old version during refactor
└── claude-code-session/           # Sub-components
    ├── MessageList.tsx
    ├── PromptQueue.tsx
    ├── SessionHeader.tsx
    ├── useCheckpoints.ts
    └── useClaudeMessages.ts
```

**Why**:
- Groups related components together
- Keeps refactored versions for reference
- Makes imports cleaner

### 4. **TypeScript Strictness is Worth It**

**Configuration** (`tsconfig.json`):
```json
{
  "strict": true,
  "noUnusedLocals": true,
  "noUnusedParameters": true,
  "noFallthroughCasesInSwitch": true
}
```

**Benefit**: Caught dozens of bugs at compile time rather than runtime.

**Pattern for unused variables**: Prefix with underscore: `_error`, `_className`

### 5. **Console Logging Strategy**

**Pattern observed** (431 console.log statements across 64 files):
- Use console.log liberally during development
- Keep trace logging in production for debugging
- Use prefixes: `[TRACE]`, `[DEBUG]`, `[ERROR]`

**Example**:
```typescript
console.log(`[TRACE] WebSocket message received:`, event.data);
console.log(`[TRACE] Parsed message:`, message);
```

**Why it works**: Desktop apps can be debugged locally, so verbose logging is acceptable and helpful.

**Future improvement**: Replace with proper logging library (winston, pino) for production.

### 6. **Error Boundaries are Essential**

**Implementation**:
- `ErrorBoundary.tsx` - Generic React error boundary
- `AnalyticsErrorBoundary.tsx` - Analytics-specific boundary

**Lesson**: Wrap major features in error boundaries to prevent full app crashes.

### 7. **React Hooks Usage Patterns**

**Statistics**: 712 hook usages across 69 files
- Most used: `useState` > `useEffect` > `useCallback` > `useMemo`

**Best practices observed**:
- Use `useCallback` for functions passed to children
- Use `useMemo` for expensive computations
- Keep `useEffect` dependencies minimal
- Extract complex effects into custom hooks

**Anti-pattern**: Avoid `useEffect` for data fetching - use custom hooks instead.

### 8. **IME Composition Handling**

**Fix** (commit `9f03d77`): Improved IME composition handling across input components.

**Why important**: Users typing in Japanese, Chinese, Korean experienced double input or lost characters.

**Pattern**:
```typescript
const [isComposing, setIsComposing] = useState(false);

return (
  <input
    onCompositionStart={() => setIsComposing(true)}
    onCompositionEnd={() => setIsComposing(false)}
    onKeyDown={(e) => {
      if (e.key === 'Enter' && !isComposing) {
        handleSubmit();
      }
    }}
  />
);
```

**Lesson**: Test with IME input methods if you have international users.

---

## Rust/Backend Lessons

### 1. **Database Schema Evolution**

**Pattern**: Store settings in key-value table for flexibility:
```rust
CREATE TABLE app_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

**Why**: Easy to add new settings without migrations.

**Used for**:
- `claude_binary_path` - User's preferred Claude installation
- `claude_installation_preference` - System vs custom preference

### 2. **Error Handling: anyhow vs Result**

**Pattern used**:
- `anyhow::Result` for complex error chains
- `Result<T, String>` for Tauri commands (simpler error messages to frontend)

**Example**:
```rust
// Internal function - detailed errors
pub fn find_claude_binary(app_handle: &AppHandle) -> Result<String, String> {
    // Complex logic with multiple error points
}

// Tauri command - simple errors
#[tauri::command]
pub async fn get_claude_binary_path(app: AppHandle) -> Result<String, String> {
    find_claude_binary(&app)
        .map_err(|e| format!("Failed to find Claude: {}", e))
}
```

**Lesson**: Use rich error types internally, convert to simple strings at the API boundary.

### 3. **Logging is Critical**

**Pattern**: Comprehensive logging throughout:
```rust
use log::{debug, error, info, warn};

info!("Searching for claude binary...");
debug!("Checking NVM directory: {:?}", nvm_dir);
warn!("Stored claude path no longer exists: {}", stored_path);
error!("Could not find claude binary in any location");
```

**Why**: Desktop apps need good logging for user support and debugging.

**Anti-pattern**: Don't use `println!` - use the `log` crate for proper logging levels.

### 4. **Process Management Patterns**

**Key learning**: Process lifecycle management is complex.

**Must handle**:
- Process spawning with proper environment
- Output streaming (stdout + stderr)
- Process termination and cleanup
- Zombie process prevention
- Session tracking

**Pattern** (from process registry):
```rust
pub struct ProcessRegistry {
    processes: Arc<Mutex<HashMap<String, Child>>>,
}

impl ProcessRegistry {
    pub fn register(&self, session_id: String, child: Child) {
        self.processes.lock().unwrap().insert(session_id, child);
    }

    pub fn kill(&self, session_id: &str) -> Result<()> {
        if let Some(mut child) = self.processes.lock().unwrap().remove(session_id) {
            child.kill()?;
        }
        Ok(())
    }
}
```

**Lesson**: Always track spawned processes and provide cleanup mechanisms.

### 5. **Regex Version Parsing**

**Pattern** from `claude_binary.rs`:
```rust
let version_regex = regex::Regex::new(
    r"(\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?(?:\+[a-zA-Z0-9.-]+)?)"
)?;
```

**Why robust**: Handles semver with pre-release and build metadata.

**Lesson**: Use regex for version extraction - it's more reliable than string manipulation.

### 6. **Cross-Platform Path Handling**

**Pattern**: Conditional compilation for platform-specific code:
```rust
#[cfg(unix)]
fn try_which_command() -> Option<ClaudeInstallation> {
    Command::new("which").arg("claude").output()
}

#[cfg(windows)]
fn try_which_command() -> Option<ClaudeInstallation> {
    Command::new("where").arg("claude").output()
}
```

**Also**: Platform-specific binary extensions (`.exe`, `.cmd` on Windows).

**Lesson**: Test on all target platforms. Path behavior differs significantly.

### 7. **Rusqlite Best Practices**

**Pattern**: Use feature flags for bundled SQLite:
```toml
rusqlite = { version = "0.32", features = ["bundled"] }
```

**Why**: Ensures consistent SQLite version across platforms.

**Query pattern**:
```rust
let value: String = conn.query_row(
    "SELECT value FROM app_settings WHERE key = ?",
    [key],
    |row| row.get(0)
)?;
```

**Anti-pattern**: Don't use string concatenation for SQL queries - always use parameter binding.

### 8. **Version Comparison Logic**

**Insight**: Don't discard installations without version info in production builds.

**Reason**: Process spawning for `--version` may be restricted in production. Presence of binary is enough.

**Pattern**:
```rust
fn select_best_installation(installations: Vec<ClaudeInstallation>) -> Option<ClaudeInstallation> {
    installations.into_iter().max_by(|a, b| {
        match (&a.version, &b.version) {
            (Some(v1), Some(v2)) => compare_versions(v1, v2),
            (Some(_), None) => Ordering::Greater,  // Prefer with version
            (None, Some(_)) => Ordering::Less,
            (None, None) => {
                // Both lack version - prefer absolute paths over "claude"
                if a.path == "claude" && b.path != "claude" {
                    Ordering::Less
                } else if a.path != "claude" && b.path == "claude" {
                    Ordering::Greater
                } else {
                    Ordering::Equal
                }
            }
        }
    })
}
```

**Lesson**: Gracefully degrade when runtime information isn't available.

---

## Build System Lessons

### 1. **Bun vs npm/yarn**

**Choice**: Bun for faster installs and builds.

**Benefits**:
- 5-10x faster than npm
- Built-in TypeScript support
- Compatible with npm ecosystem

**Gotcha**: Some developers may not have Bun installed - document this clearly.

### 2. **Vite Configuration**

**Key settings** from `vite.config.ts`:

```typescript
{
  server: {
    port: 1420,        // Fixed port for Tauri
    strictPort: true,  // Fail if port unavailable
    watch: {
      ignored: ["**/src-tauri/**"]  // Don't watch Rust files
    }
  },
  build: {
    chunkSizeWarningLimit: 2000,  // Increased for vendor chunks
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': [...],  // Separate Radix UI components
          'tauri': [...],      // Tauri APIs separate
        }
      }
    }
  }
}
```

**Why manual chunks**: Better caching, faster incremental builds, smaller initial bundle.

**Lesson**: Configure code splitting early - it's harder to add later.

### 3. **Cargo Workspace Structure**

**Pattern**: Single package with multiple binaries:
```toml
[package]
name = "opcode"
default-run = "opcode"

[[bin]]
name = "opcode"
path = "src/main.rs"

[[bin]]
name = "opcode-web"
path = "src/web_main.rs"

[lib]
name = "opcode_lib"
crate-type = ["lib", "cdylib", "staticlib"]
```

**Why this structure**:
- Shared code in `lib.rs`
- Two different entry points
- Can be used as a library

**Lesson**: `default-run` is essential for multi-binary projects.

### 4. **CI/CD Learnings**

**Fix** (commit `032ee2a`): Use `oven-sh/setup-bun@v2` to fix Bun download issues on ubuntu-24.04.

**Lesson**: Pin action versions and test on all target platforms in CI.

### 5. **Development Scripts**

**Best practice**: Document all build commands in justfile:
```justfile
# Quick development cycle
quick: build-frontend
    cd src-tauri && cargo run

# Web server for mobile access
web: build-frontend
    cd src-tauri && cargo run --bin opcode-web

# Get local IP for phone testing
ip:
    @ip route get 1.1.1.1 | grep -oP 'src \K\S+'
```

**Why**: Self-documenting workflow, consistent commands across team.

### 6. **Build Order Matters**

**Critical sequence**:
1. `bun install` - Install dependencies
2. `bun run build` - Build frontend to `dist/`
3. `cargo run` - Run Tauri app

**Why this order**: Tauri expects frontend to be built, won't build it automatically.

**Anti-pattern**: Running `tauri dev` without building frontend first will fail with "dist/ doesn't exist" error.

---

## Process Management Lessons

### 1. **Child Process Environment**

**Critical lesson**: Child processes don't inherit full environment.

**Must explicitly pass**:
- `PATH` - For finding executables
- `HOME` - For user home directory
- `NVM_BIN` - For NVM node installations
- `HOMEBREW_PREFIX` - For Homebrew installations
- Proxy variables (`HTTP_PROXY`, `HTTPS_PROXY`)

**Pattern**: See `create_command_with_env()` in `claude_binary.rs`.

### 2. **Stream Handling**

**Pattern**: Capture both stdout and stderr:
```rust
let mut child = Command::new(program)
    .stdout(Stdio::piped())
    .stderr(Stdio::piped())
    .spawn()?;

// Spawn tasks to read both streams
let stdout_task = tokio::spawn(async move {
    // Read and forward stdout
});

let stderr_task = tokio::spawn(async move {
    // Read and forward stderr
});
```

**Gotcha**: Web server currently only captures stdout (documented in web_server.design.md as a known issue).

### 3. **Process Cleanup**

**Must implement**:
- Process registry to track all spawned processes
- Cleanup on app shutdown
- Cleanup on session cancellation
- Zombie process prevention

**Anti-pattern**: Don't spawn processes without tracking them - leads to orphaned processes.

### 4. **Timeouts**

**Pattern from tests**: Use platform-specific timeout commands:
```rust
#[cfg(target_os = "macos")]
const TIMEOUT_CMD: &str = "gtimeout";

#[cfg(target_os = "linux")]
const TIMEOUT_CMD: &str = "timeout";

Command::new(TIMEOUT_CMD)
    .arg("20s")
    .arg("claude")
    .args(args)
    .spawn()
```

**Lesson**: Always have timeouts for external process calls to prevent hangs.

---

## Testing Lessons

### 1. **Real vs Mock Testing**

**Major decision** (TESTS_COMPLETE.md): Use real Claude commands, not mocks.

**Why real testing**:
- Tests validate actual behavior
- End-to-end validation
- No mock drift
- Catches integration issues

**Trade-off**: Tests are slower but more reliable.

**Pattern**:
```rust
fn execute_claude_task(task: &str) -> ClaudeOutput {
    Command::new("claude")
        .arg("--dangerously-skip-permissions")
        .arg(task)
        .output()
        .expect("Failed to execute claude")
}
```

**Lesson**: Use real commands when possible, mocks only when unavoidable (network, paid APIs, etc.).

### 2. **Test Organization**

**Structure**:
```
src-tauri/tests/
├── TESTS_COMPLETE.md     # Test status documentation
├── TESTS_TASK.md         # Test implementation notes
├── claude_real.rs        # Real Claude execution helpers
└── integration_test.rs   # Integration tests
```

**Why**: Tests are documentation - document what they test and why.

### 3. **Platform-Aware Tests**

**Pattern**: Different expectations for different platforms:
```rust
#[cfg(target_os = "macos")]
assert!(output.success);

#[cfg(target_os = "linux")]
assert!(output.stdout.len() > 0);

#[cfg(target_os = "windows")]
assert!(output.stderr.is_empty());
```

**Why**: Behavior differs across platforms - tests must accommodate this.

### 4. **Test Timeouts**

**Pattern**: 20-second timeout for Claude commands:
```rust
Command::new("gtimeout")
    .arg("20s")
    .arg("claude")
    .spawn()
```

**Why**: Claude needs time to respond. Too short = flaky tests. Too long = slow CI.

**Lesson**: Tune timeouts based on actual command execution time.

### 5. **No Ignored Tests**

**Principle**: Fix broken tests, don't ignore them.

**From TESTS_COMPLETE.md**: "0 ignored" - all tests either pass or are removed.

**Lesson**: Ignored tests become stale and eventually useless. Fix or delete.

---

## Performance Lessons

### 1. **Code Splitting**

**Implementation**: Manual chunks in Vite config (see Build System section).

**Impact**:
- Faster initial load
- Better caching
- Smaller main bundle

**Lesson**: Set up code splitting early - it's architectural, not cosmetic.

### 2. **React Rendering Optimization**

**Patterns used**:
- `React.memo` for expensive components
- `useCallback` for stable function references
- `useMemo` for expensive computations
- Custom hooks with proper dependencies

**Example**:
```typescript
const MemoizedMessageList = React.memo(MessageList, (prev, next) => {
  return prev.messages.length === next.messages.length;
});
```

### 3. **Debouncing User Input**

**Pattern**: `useDebounce.ts` hook:
```typescript
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}
```

**Use cases**: Search inputs, auto-save, API calls.

### 4. **Pagination**

**Pattern**: `usePagination.ts` hook handles pagination logic.

**Why**: Large lists (sessions, agents) need pagination for performance.

**Lesson**: Implement pagination from start for lists that could grow large.

### 5. **Performance Monitoring**

**Tool**: `usePerformanceMonitor.ts` hook tracks render times.

**Usage**: Wrap expensive components to identify bottlenecks.

**Lesson**: Measure before optimizing - don't guess where the slowness is.

---

## Security Lessons

### 1. **Never Log Sensitive Data**

**Pattern**: Check all log statements for:
- API keys
- Tokens
- Passwords
- User credentials
- File contents (may contain secrets)

**Anti-pattern**: Logging entire request/response objects without sanitization.

### 2. **SQL Injection Prevention**

**Always use parameter binding**:
```rust
// ✅ Good
conn.execute("SELECT * FROM users WHERE id = ?", [id])?;

// ❌ Bad
conn.execute(&format!("SELECT * FROM users WHERE id = {}", id))?;
```

### 3. **File System Access**

**Pattern**: Validate all file paths:
```rust
let path = PathBuf::from(user_path);
if !path.starts_with(&safe_root) {
    return Err("Path traversal attempt detected");
}
```

**Lesson**: Never trust user-provided paths - always validate against allowed directories.

### 4. **Process Execution Security**

**Consideration**: `--dangerously-skip-permissions` flag bypasses Claude's safety checks.

**When acceptable**:
- Development and testing
- Trusted user-controlled environments
- Desktop app where user explicitly grants permissions

**When NOT acceptable**:
- Web server mode with multiple users
- Production SaaS deployment
- Untrusted input

**Lesson**: Document security trade-offs clearly.

### 5. **Web Server Security Issues**

**Documented in web_server.design.md**:
- CORS allows all origins (development only)
- No authentication (not production-ready)
- Session isolation broken (critical bug)

**Lesson**: Document known security issues clearly. Don't ship to production without fixing them.

### 6. **Environment Variable Handling**

**Pattern**: Only pass specific, known environment variables to child processes.

**Why**: Prevents leaking sensitive environment variables to untrusted code.

**Implementation**: Whitelist approach in `create_command_with_env()`.

---

## Developer Experience Lessons

### 1. **Comprehensive Documentation**

**Success**: CLAUDE.md contains everything needed to understand the project.

**Includes**:
- Quick start guide
- Project architecture
- Common issues and fixes
- Development workflow
- Installation history
- Configuration deep dives

**Lesson**: Treat documentation as first-class code. Update it with every major change.

### 2. **Self-Documenting Commands**

**Pattern**: justfile with descriptions:
```justfile
# Quick development cycle: build frontend and run
quick: build-frontend
    cd src-tauri && cargo run

# Run web server mode for phone access
web: build-frontend
    cd src-tauri && cargo run --bin opcode-web
```

**Why**: New developers can run `just` and see all available commands.

### 3. **Troubleshooting Section**

**Must have**:
- Common error messages
- Platform-specific issues
- Resolution steps
- When to seek help

**Example from CLAUDE.md**:
```
### "cargo not found"
source "$HOME/.cargo/env"

### "dist/ doesn't exist"
bun run build
```

**Lesson**: Document every error you encounter - you'll see it again.

### 4. **Git Commit Messages**

**Pattern observed**: Conventional commits with detailed descriptions:
```
fix(input): improve IME composition handling across input components

refactor: rename claudia to opcode throughout web server code
- Rename binary from claudia-web to opcode-web in Cargo.toml
- Update all references in justfile (web commands)
- Update console output messages in web_server.rs and web_main.rs

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

**Best practices**:
- Use type prefix (fix, feat, refactor, chore, docs)
- Clear one-line summary
- Detailed bullet points
- Attribution when AI-assisted

**Lesson**: Good commit messages are documentation - they explain WHY, not just what.

### 5. **Project Renaming Strategy**

**Pattern**: Three major renames in project history:
1. Claudia → Gooey
2. Gooey → opcode
3. claudia-web → opcode-web

**Systematic approach** (commit `e3fff0d`):
- Update Cargo.toml
- Update justfile
- Update all references in code
- Update documentation
- Single atomic commit

**Lesson**: Rename everything at once in one commit to avoid inconsistent state.

### 6. **Keep Old Code During Refactor**

**Pattern**:
- `ClaudeCodeSession.tsx` - Current version
- `ClaudeCodeSession.refactored.tsx` - New modular version
- `App.tsx` vs `App.cleaned.tsx`

**Why**:
- Can compare implementations
- Roll back if refactor fails
- Learn from both versions

**Lesson**: Don't delete old code immediately during major refactors.

---

## Debugging Wisdom

### 1. **Comprehensive Logging Strategy**

**Pattern**: Log at every boundary:
```typescript
console.log(`[TRACE] WebSocket opened successfully`);
console.log(`[TRACE] Sending request:`, request);
console.log(`[TRACE] Parsed message:`, message);
console.log(`[TRACE] Dispatching event:`, event.detail);
```

**Why**: Trace the entire data flow through the system.

**Levels**:
- `[TRACE]` - Detailed execution flow
- `[DEBUG]` - Debug information
- `[INFO]` - Important events
- `[WARN]` - Warnings
- `[ERROR]` - Errors

### 2. **State Inspection Points**

**Pattern**: Log state before and after operations:
```rust
info!("Before: installations = {:?}", installations);
installations.sort_by(|a, b| ...);
info!("After: installations = {:?}", installations);
```

**Why**: Identify where data transforms incorrectly.

### 3. **Network Debugging**

**For WebSocket issues**:
- Log connection open/close
- Log every message sent/received
- Log parsed message structure
- Log event dispatch

**Example**:
```typescript
ws.onopen = () => {
  console.log(`[TRACE] WebSocket opened`);
};

ws.onmessage = (event) => {
  console.log(`[TRACE] Received:`, event.data);
  const parsed = JSON.parse(event.data);
  console.log(`[TRACE] Parsed:`, parsed);
};
```

### 4. **Platform-Specific Debugging**

**Pattern**: Log platform info:
```rust
info!("Platform: {}", std::env::consts::OS);
info!("Arch: {}", std::env::consts::ARCH);
info!("Environment: {:?}", std::env::vars().collect::<Vec<_>>());
```

**Why**: Behavior differs by platform - need context to debug.

### 5. **Event Debugging**

**Pattern**: Log event registration and firing:
```typescript
console.log(`[TRACE] Registering listener for: ${eventName}`);

window.addEventListener(eventName, (event) => {
  console.log(`[TRACE] Event fired: ${eventName}`, event.detail);
});
```

**Why**: Event-driven code is hard to debug without visibility into event flow.

---

## Refactoring Lessons

### 1. **Refactor in Small Steps**

**Success story**: ClaudeCodeSession refactor (commit `cb7599e`)
- First: Extract hooks (`useClaudeMessages`, `useCheckpoints`)
- Then: Extract UI components (`MessageList`, `PromptQueue`)
- Finally: Create refactored version with new structure

**Why**: Small steps are easier to test and review.

**Lesson**: Don't refactor everything at once. One concern at a time.

### 2. **Keep Tests Passing**

**Principle**: After every refactor step, all tests should pass.

**Why**: Ensures refactor didn't break functionality.

**If tests fail**: Either fix the refactor or fix the tests immediately.

**Lesson**: Refactoring is NOT adding features. Tests should pass without changes.

### 3. **Remove Dead Code**

**Pattern from commit `11c24e7`**: "Remove unused props/imports and delegate project path selection to tabs"

**What was removed**:
- Unused icons/components
- Dead handlers (e.g., unused directory selection)
- Unused callbacks (`onBack`, `onMCPClick`, `onUsageClick`)
- Unused TypeScript variables (rename to `_error`, `_className`)

**Why**: Dead code confuses new developers and increases maintenance burden.

**Lesson**: Delete aggressively. If it's not used, remove it.

### 4. **Simplify Before Optimizing**

**Example**: Process registry refactor (commit `16acda5`) simplified registration before optimizing.

**Why**: Simple code is easier to optimize than complex code.

**Lesson**: Make it work, make it simple, then make it fast.

### 5. **Extract, Don't Rewrite**

**Pattern**: Extract functionality into new modules while keeping old code working.

**Example**: `apiAdapter.ts` extracted environment detection without breaking existing API calls.

**Why**: Rewriting from scratch loses institutional knowledge and introduces new bugs.

**Lesson**: Extract and refactor > rewrite from scratch.

---

## Technical Debt Lessons

### 1. **Document Debt Immediately**

**Pattern**: web_server.design.md has "Critical Issues Still Remaining" section.

**What's documented**:
- Session-scoped event dispatching (CRITICAL)
- Process cancellation not implemented (CRITICAL)
- stderr not captured (MEDIUM)
- Missing claude-cancelled events (MEDIUM)

**Why document**:
- Prevents shipping broken features
- Helps prioritize fixes
- Warns future developers

**Lesson**: If you can't fix it now, at least document it with severity.

### 2. **TODO Comments Pattern**

**Current state**: 17 TODOs in codebase (mostly in UI components).

**Good TODO**:
```typescript
// TODO: Implement toast notification
// Context: Need to add react-toastify dependency first
// Priority: Medium
// Issue: #123
```

**Bad TODO**:
```typescript
// TODO: fix this
```

**Lesson**: TODOs should explain what, why, and how to fix. Otherwise they're useless.

### 3. **Known Issues vs Bugs**

**Known issues**: Documented in design docs (like web_server.design.md).

**Bugs**: Tracked in issue tracker.

**Difference**:
- Known issues are architectural limitations
- Bugs are unintended behavior

**Lesson**: Communicate which is which - users need to know if something is "broken" or "not implemented yet".

### 4. **Cleanup as You Go**

**Example from commit `abc7323`**: "Clean up code and remove TODO comments"

**Why**: Regular cleanup prevents debt accumulation.

**Pattern**:
- Every sprint, allocate time for cleanup
- Remove obsolete comments
- Update outdated documentation
- Fix small issues

**Lesson**: Small, regular cleanups > big refactor later.

### 5. **The 80/20 Rule**

**Observation**: 80% of functionality uses 20% of code.

**Applied**:
- Removed bundled binary support (20% of code, rarely used)
- Simplified web server (focus on single-session use case first)

**Lesson**: Cut features that add complexity but little value.

---

## Do's and Don'ts

### Architecture

✅ **DO**:
- Design for both Tauri and web from the start
- Use unified API adapters (`apiAdapter.ts`)
- Keep business logic in shared modules
- Document unusual architectural choices

❌ **DON'T**:
- Assume Tauri has standard hot-reload workflow
- Bundle binaries unless absolutely necessary
- Mix UI and business logic in components
- Build desktop-only features without web consideration

### Code Organization

✅ **DO**:
- Extract reusable logic into hooks early
- Group related components in subdirectories
- Keep refactored code during transitions
- Use TypeScript strict mode
- Add path aliases (`@/`) for imports

❌ **DON'T**:
- Create 1000+ line components
- Put all components in one flat directory
- Delete old code immediately during refactors
- Disable TypeScript checks to "fix" errors
- Use relative imports for distant modules

### State Management

✅ **DO**:
- Use Context for global, cross-cutting concerns
- Use local state for UI-only concerns
- Extract complex state to custom hooks
- Optimize with `useCallback` and `useMemo`

❌ **DON'T**:
- Lift all state to Context (causes re-renders)
- Use Redux for everything
- Pass callbacks through many component layers
- Optimize prematurely

### Error Handling

✅ **DO**:
- Wrap features in error boundaries
- Log errors with context
- Return user-friendly error messages
- Handle all Result types explicitly in Rust

❌ **DON'T**:
- Let errors crash the entire app
- Log error objects without message
- Return stack traces to users
- Use `.unwrap()` in production Rust code

### Testing

✅ **DO**:
- Use real commands when possible
- Test on all target platforms
- Document what each test validates
- Keep all tests passing
- Add timeouts for external processes

❌ **DON'T**:
- Mock everything
- Test only on your development machine
- Ignore failing tests
- Write tests without assertions
- Let tests run forever

### Build & Deploy

✅ **DO**:
- Document build order clearly
- Use justfile for common commands
- Configure code splitting early
- Pin dependency versions in CI
- Test production builds locally

❌ **DON'T**:
- Assume developers know the build workflow
- Require manual, undocumented steps
- Skip code splitting
- Use `latest` tags in CI
- Only test development builds

### Documentation

✅ **DO**:
- Document unusual patterns immediately
- Keep troubleshooting section up to date
- Explain WHY, not just WHAT
- Update docs with code changes
- Include examples in docs

❌ **DON'T**:
- Write "self-documenting code" only
- Let docs go stale
- Document implementation details only
- Write docs separate from code changes
- Use only text - add diagrams

### Security

✅ **DO**:
- Validate all user inputs
- Use parameter binding for SQL
- Whitelist environment variables
- Document security trade-offs
- Review code for sensitive data logging

❌ **DON'T**:
- Trust user-provided paths
- Use string concatenation for SQL
- Pass all environment variables to children
- Skip security review
- Log tokens, passwords, keys

---

## External Resources

### Official Documentation

1. **Tauri v2 Documentation**
   - https://tauri.app/
   - Essential reading for understanding Tauri's architecture
   - Covers IPC, window management, security model

2. **Bun Documentation**
   - https://bun.sh/
   - Fast JavaScript runtime and package manager
   - Used throughout project for speed

3. **Cargo Documentation**
   - https://doc.rust-lang.org/cargo/
   - Especially: [Manifest Format](https://doc.rust-lang.org/cargo/reference/manifest.html)
   - Key for understanding `default-run` and multi-binary projects

4. **Vite Documentation**
   - https://vitejs.dev/
   - Focus on: build optimization, code splitting, plugin system

### Community Resources

5. **GitHub - tauri-apps/tauri Discussions**
   - https://github.com/tauri-apps/tauri/discussions
   - Discussion #7592 helped solve multiple binaries issue

6. **Stack Overflow**
   - Search: "tauri multiple binaries"
   - Search: "rust cargo default-run"
   - Found solutions that documentation didn't cover

### React Best Practices

7. **React TypeScript Cheatsheet**
   - https://react-typescript-cheatsheet.netlify.app/
   - Patterns for hooks, context, error boundaries

8. **Kent C. Dodds Blog**
   - https://kentcdodds.com/blog
   - Especially: "Application State Management", "How to use React Context effectively"

### Rust Learning

9. **Rust Book**
   - https://doc.rust-lang.org/book/
   - Chapters on Error Handling and Smart Pointers most relevant

10. **Rust by Example**
    - https://doc.rust-lang.org/rust-by-example/
    - Practical examples for process spawning, file I/O

### Tools Recommended

11. **just** - Command runner
    - https://github.com/casey/just
    - Better than Makefile for development commands

12. **cargo-watch** - Auto-rebuild
    - `cargo install cargo-watch`
    - Run: `cargo watch -x run`

13. **bunx** - Run packages
    - Built into Bun
    - Example: `bunx tsc --noEmit`

### Design Patterns

14. **Patterns.dev**
    - https://www.patterns.dev/
    - React patterns, performance patterns

15. **Rust Design Patterns**
    - https://rust-unofficial.github.io/patterns/
    - Especially: Builder pattern, Newtype pattern

---

## Future Recommendations

### High Priority

1. **Fix Web Server Critical Issues**
   - Session-scoped event dispatching
   - Process cancellation implementation
   - stderr capture
   - See web_server.design.md for details

2. **Implement Proper Logging Library**
   - Replace console.log with structured logging
   - Use winston or pino for frontend
   - Use tracing crate for Rust backend
   - Add log levels, rotation, filtering

3. **Add Comprehensive Tests**
   - Frontend unit tests (React Testing Library)
   - Frontend integration tests (Playwright)
   - More Rust integration tests
   - E2E tests for critical flows

4. **Performance Optimization**
   - Implement virtual scrolling for long lists
   - Add service worker for web mode
   - Optimize bundle size (currently large)
   - Add performance budgets

### Medium Priority

5. **State Management Refactor**
   - Implement Zustand stores (examples exist in `src/stores/`)
   - Remove prop drilling
   - Centralize session and agent state

6. **Error Handling Improvements**
   - Add toast notification system
   - Better error messages to users
   - Retry logic for failed API calls
   - Offline mode support

7. **Developer Experience**
   - Add pre-commit hooks (lint, format, type-check)
   - Set up Storybook for component development
   - Add development Docker container
   - Improve hot-reload workflow

8. **Documentation**
   - Add architecture diagrams
   - Record video tutorials
   - Create contributor guide
   - Add API documentation

### Low Priority

9. **UI/UX Polish**
   - Add loading skeletons
   - Improve empty states
   - Add animations/transitions
   - Mobile responsiveness improvements

10. **Feature Additions**
    - Authentication system
    - Multi-user support
    - Cloud sync
    - Plugin system

### Infrastructure

11. **CI/CD Improvements**
    - Add automated release notes
    - Implement semantic versioning
    - Add performance benchmarking in CI
    - Set up automated security scanning

12. **Monitoring**
    - Add error tracking (Sentry)
    - Add analytics (PostHog already integrated)
    - Add performance monitoring
    - Set up alerts

### Security Hardening

13. **Security Review**
    - Third-party security audit
    - Implement CSP (Content Security Policy)
    - Add rate limiting for web server
    - Implement authentication for web mode

14. **Compliance**
    - GDPR compliance review
    - Add privacy policy
    - Implement data export
    - Add data deletion

---

## Advice for Contributors

### Getting Started

1. **Read CLAUDE.md first** - It contains the project's unusual workflow
2. **Build the project** - Follow exact steps in order
3. **Run the web server** - Test both desktop and web modes
4. **Check existing issues** - Don't duplicate work

### Before Submitting PR

1. **Test on all platforms** - macOS, Linux, Windows
2. **Run type checking** - `bunx tsc --noEmit`
3. **Format code** - `cargo fmt` for Rust
4. **Update documentation** - If you changed workflow or architecture
5. **Add tests** - For new features
6. **Check CONTRIBUTING.md** - Follow PR guidelines

### Code Review Guidelines

**For reviewers**:
- Check for security issues first
- Verify tests are added
- Ensure documentation is updated
- Look for performance issues
- Check error handling

**For contributors**:
- Respond to feedback promptly
- Don't take criticism personally
- Ask questions if unclear
- Update PR based on feedback
- Add comments explaining complex logic

### Communication

1. **Use issue templates** - Provide necessary context
2. **Be specific** - "Button doesn't work" → "Submit button in agent creation form throws error when clicked"
3. **Provide reproduction steps** - How to reproduce the issue
4. **Include logs** - Error messages, console output
5. **Be respectful** - Everyone is here to help

### Learning the Codebase

**Start with**:
1. `README.md` - Overview
2. `CLAUDE.md` - Deep dive into architecture
3. `web_server.design.md` - Web server specifics
4. `docs/lessons-learned.md` - This document

**Then explore**:
1. `src/lib/apiAdapter.ts` - How dual-mode works
2. `src-tauri/src/claude_binary.rs` - Binary detection
3. `src/components/ClaudeCodeSession.tsx` - Main session component
4. `src-tauri/src/web_server.rs` - Web server implementation

**Practice by**:
1. Fixing a "good first issue"
2. Adding a small feature
3. Improving documentation
4. Adding tests

### Common Pitfalls

1. **Forgetting to build frontend** - Always `bun run build` first
2. **Not testing web mode** - Test both Tauri and web
3. **Breaking existing features** - Run full test suite
4. **Incomplete error handling** - Handle all error cases
5. **Missing documentation** - Update docs with code

---

## References

- [Tauri Documentation](https://tauri.app/)
- [Bun Documentation](https://bun.sh/)
- [Cargo default-run documentation](https://doc.rust-lang.org/cargo/reference/manifest.html)
- See `web_server.design.md` for web server architecture details
- See `README.md` for full project documentation
- See `justfile` for intended build workflow
- See `CLAUDE.md` for project-specific documentation

---

## Conclusion

This document represents the accumulated wisdom from building Opcode. The lessons here were learned through trial and error, careful research, and thoughtful refactoring.

Key takeaways:

1. **Research first, code second** - Don't assume you know the answer
2. **Test thoroughly** - Manual testing prevents automated disasters
3. **Document everything** - Your future self will thank you
4. **Build-first workflow is intentional** - Don't fight the architecture
5. **Dual-mode support is complex** - Design for it from the start
6. **Real testing > Mocking** - Test the actual behavior
7. **Simplify before optimizing** - Simple code is maintainable code
8. **Security can't be an afterthought** - Review every feature
9. **Technical debt compounds** - Address it regularly
10. **The community has answers** - Search before implementing

Remember: This project has an unusual architecture by design. Understanding the "why" behind these decisions will help you work effectively within the codebase.

If you find new lessons, add them here. This is a living document that should grow with the project.

---

**Last updated**: 2025-10-20
**Contributors**: Max, Claude Code, Project Team
