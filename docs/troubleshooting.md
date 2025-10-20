# Runtime Troubleshooting Guide

This comprehensive guide covers runtime errors, process management issues, and debugging techniques for Opcode after installation.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Process Management Issues](#process-management-issues)
3. [WebSocket & Communication Failures](#websocket--communication-failures)
4. [Database & Storage Errors](#database--storage-errors)
5. [Frontend-Backend Connection Issues](#frontend-backend-connection-issues)
6. [Claude Code Integration Problems](#claude-code-integration-problems)
7. [Checkpoint & Timeline Errors](#checkpoint--timeline-errors)
8. [Agent Execution Failures](#agent-execution-failures)
9. [Performance & Resource Problems](#performance--resource-problems)
10. [Web Server Mode Issues](#web-server-mode-issues)
11. [Diagnostic Commands](#diagnostic-commands)
12. [Emergency Recovery Procedures](#emergency-recovery-procedures)
13. [Log Files & Debugging](#log-files--debugging)

---

## Installation Issues

### "cargo not found"
**Symptoms**: Application fails to start or build with "cargo not found" error.

**Causes**:
- Cargo environment not loaded in shell session
- Cargo not installed or installation incomplete

**Solutions**:
```bash
# Temporary fix (current session only)
source "$HOME/.cargo/env"

# Permanent fix - add to ~/.zshrc or ~/.bashrc
echo 'source "$HOME/.cargo/env"' >> ~/.zshrc
source ~/.zshrc
```

### "bun not found"
**Symptoms**: Cannot run `bun` commands, build fails.

**Causes**:
- Bun not in PATH
- Shell not reloaded after installation

**Solutions**:
```bash
# Restart shell
exec /bin/zsh  # or exec /bin/bash

# Verify bun installation
which bun
bun --version

# If not found, reinstall
curl -fsSL https://bun.sh/install | bash
```

### "dist/ doesn't exist"
**Symptoms**: Tauri fails to start with "frontendDist doesn't exist" error.

**Causes**:
- Frontend not built before running Tauri
- Build artifacts deleted

**Solutions**:
```bash
# Build frontend
bun run build

# Verify dist directory exists
ls -la dist/

# Then run Tauri
bun run tauri dev
```

### Multiple binary error
**Symptoms**: `cargo run` shows "could not determine which binary to run".

**Causes**:
- Project defines multiple binaries (`opcode` and `opcode-web`)
- No default binary specified

**Solutions**:
1. Verify `default-run = "opcode"` is in `src-tauri/Cargo.toml` under `[package]` section
2. Or specify binary explicitly:
```bash
cargo run --bin opcode      # Desktop app
cargo run --bin opcode-web  # Web server
```

---

## Process Management Issues

### Claude Process Won't Start
**Symptoms**:
- "Failed to spawn Claude" error
- Process starts but immediately exits
- No output from Claude commands

**Causes**:
- Claude binary not found or wrong path
- Permissions issues
- Missing Node.js/npm environment
- Claude not in PATH for macOS apps

**Solutions**:

1. **Verify Claude Installation**:
```bash
# Check if Claude is in PATH
which claude

# Check version
claude --version

# If using NVM, ensure NVM_BIN is set
echo $NVM_BIN
```

2. **Check Binary Detection**:
- Desktop app: Settings → Check Claude Version
- Logs will show where it's looking for Claude binary
- Check `/Users/max/local/opcode/src-tauri/src/claude_binary.rs` discovery logic

3. **Manual Path Override**:
```bash
# Find your Claude installation
find /usr/local/bin /opt/homebrew/bin ~/.nvm ~/.local/bin -name claude 2>/dev/null

# Set custom path in app settings database:
# Settings → Advanced → Claude Binary Path
```

4. **Permissions Check**:
```bash
# Ensure Claude is executable
ls -l $(which claude)

# Should show: -rwxr-xr-x
# If not:
chmod +x /path/to/claude
```

### Process Stuck/Hanging
**Symptoms**:
- Claude process running but no output
- UI shows "running" indefinitely
- CPU usage stuck at constant level

**Causes**:
- Process waiting for input
- Deadlock in I/O streams
- WebSocket connection lost
- Process registry not updated

**Diagnostic Steps**:
```bash
# List running Claude processes
ps aux | grep claude

# Check process status
# Desktop: View → Running Sessions
# Or check process registry
```

**Solutions**:

1. **Cancel via UI**: Click cancel button in session view
2. **Force Kill**:
```bash
# Get PID from UI or ps command
kill -TERM <pid>

# If TERM doesn't work
kill -KILL <pid>

# Kill all Claude processes (last resort)
pkill -f claude
```

3. **Clear Process Registry**:
- Restart application
- Check `~/.local/opcode/agents.db` for stale entries

### Process Cleanup Failures
**Symptoms**:
- Zombie processes remain after cancellation
- "Process already running" error
- Process count keeps growing

**Causes**:
- ProcessRegistry not cleaning up properly
- Child process handles not released
- PID reuse causing conflicts

**Solutions**:

1. **Manual Cleanup**:
```bash
# Find and kill orphaned processes
ps aux | grep claude | grep -v grep | awk '{print $2}' | xargs kill

# Clean up finished processes via API
# (Tauri command: cleanup_finished_processes)
```

2. **Restart Application** to reset process registry

3. **Check Logs** at `/Users/max/local/opcode/src-tauri/target/debug/` for process lifecycle errors

---

## WebSocket & Communication Failures

### WebSocket Connection Drops
**Symptoms**:
- Real-time updates stop
- "WebSocket disconnected" in console
- Session output freezes mid-execution

**Causes**:
- Network interruption
- Web server restart
- Browser closed WebSocket
- Server timeout

**Solutions**:

1. **Desktop Mode**: Uses Tauri events, not WebSockets - should reconnect automatically
2. **Web Server Mode**:
   - Refresh browser page
   - Check server logs for errors
   - Verify firewall not blocking WebSocket connections

3. **Check Connection**:
```bash
# Desktop app - check Tauri event system
# Web server - check WebSocket endpoint
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: $(openssl rand -base64 16)" \
     http://localhost:8080/ws/claude
```

### Event Emission Failures
**Symptoms**:
- Frontend not receiving backend events
- `claude-output` events missing
- `claude-complete` never fires

**Causes**:
- Event listener not registered
- Session ID mismatch
- Event name typo
- Tauri event system error

**Solutions**:

1. **Check Event Names**:
   - Generic: `claude-output`, `claude-complete`, `claude-cancelled`
   - Session-specific: `claude-output:{session_id}`, `claude-complete:{session_id}`

2. **Verify Session ID**:
   - Check frontend matches backend session ID
   - Look for UUID format mismatches

3. **Debug Events**:
```javascript
// In browser console
window.__TAURI__.event.listen('claude-output', (event) => {
  console.log('Received event:', event.payload);
});
```

### Session Isolation Failures (Web Server)
**Symptoms**:
- Multiple users see each other's output
- Sessions interfere with each other
- Wrong session receives events

**Known Issue**: This is a documented bug in `web_server.design.md`:
- Session-scoped event dispatching is BROKEN
- Events are global, not session-specific
- **Workaround**: Use web server for single user/single session only
- **Status**: Not production-ready for multi-user scenarios

---

## Database & Storage Errors

### SQLite Database Locked
**Symptoms**:
- "Database is locked" error
- Operations timeout
- Agent CRUD operations fail

**Causes**:
- Multiple processes accessing same database
- Long-running transaction not committed
- File system lock not released
- Database file corruption

**Solutions**:

1. **Check Running Processes**:
```bash
# Find processes using database
lsof ~/.local/opcode/agents.db

# Or on Linux:
fuser ~/.local/opcode/agents.db
```

2. **Close Other Instances**:
- Quit other Opcode instances
- Check for background processes

3. **Database Recovery**:
```bash
# Backup current database
cp ~/.local/opcode/agents.db ~/.local/opcode/agents.db.backup

# Check integrity
sqlite3 ~/.local/opcode/agents.db "PRAGMA integrity_check;"

# If corrupted, restore from backup or reset
```

4. **WAL Mode Issues**:
```bash
# Check WAL file
ls -la ~/.local/opcode/agents.db-wal

# Force checkpoint
sqlite3 ~/.local/opcode/agents.db "PRAGMA wal_checkpoint(TRUNCATE);"
```

### Storage Directory Permissions
**Symptoms**:
- "Permission denied" when creating agents
- Cannot write to database
- Settings not persisting

**Solutions**:
```bash
# Check permissions
ls -la ~/.local/opcode/

# Fix ownership
chown -R $USER ~/.local/opcode/

# Fix permissions
chmod -R u+rw ~/.local/opcode/
```

### Database Schema Mismatch
**Symptoms**:
- "No such column" errors
- Migration failures
- App crashes on startup

**Solutions**:

1. **Check App Version**: Ensure using latest compatible version
2. **Reset Database** (DESTRUCTIVE):
```bash
# Backup first!
mv ~/.local/opcode/agents.db ~/.local/opcode/agents.db.old

# Restart app - new database will be created
```

3. **Manual Migration**: Check migration scripts in `src-tauri/src/commands/storage.rs`

---

## Frontend-Backend Connection Issues

### Tauri API Call Failures
**Symptoms**:
- "Failed to invoke command" errors
- Timeouts on API calls
- No response from backend

**Causes**:
- Command name mismatch
- Serialization errors
- Backend panic/crash
- CORS issues (web server mode)

**Diagnostic Steps**:

1. **Check Command Registration**: In `src-tauri/src/lib.rs`, verify command is registered
2. **Check Arguments**:
```javascript
// Frontend - ensure parameters match Rust signature
await invoke('command_name', {
  parameterName: value  // Use camelCase in JS, snake_case in Rust
});
```

3. **Backend Logs**: Check console output for Rust panics

### JSON Serialization Errors
**Symptoms**:
- "Failed to deserialize" errors
- Type mismatch errors
- API calls return null/undefined

**Solutions**:

1. **Verify Data Types**: Match TypeScript types to Rust structs
2. **Check Null Handling**: Rust Option types require null checking
3. **Debug Payload**:
```javascript
console.log('Sending to backend:', JSON.stringify(payload, null, 2));
```

### API Adapter Issues
**Symptoms**:
- Web server mode works, desktop doesn't (or vice versa)
- API calls routing to wrong backend

**Causes**:
- `apiAdapter.ts` detection logic failing
- Environment variable mismatch

**Solutions**:
Check `/Users/max/local/opcode/src/lib/apiAdapter.ts` for mode detection logic.

---

## Claude Code Integration Problems

### Binary Not Found
**Symptoms**:
- "Claude binary not found" error
- `check_claude_version` returns `is_installed: false`
- Execution commands fail immediately

**Causes**:
- Claude Code not installed
- Not in PATH
- Wrong installation directory
- NVM/Homebrew path issues

**Solutions**:

1. **Installation Detection**:
```bash
# Check all searched locations
ls -l /usr/local/bin/claude
ls -l /opt/homebrew/bin/claude
ls -l ~/.local/bin/claude
ls -l ~/.nvm/versions/node/*/bin/claude

# Check which is used
just show-claude-path
```

2. **Install Claude Code**:
```bash
# Via npm
npm install -g claude-code

# Via Homebrew
brew install anthropic/claude/claude-code

# Verify
claude --version
```

3. **PATH Issues on macOS**:
   - macOS apps have restricted PATH
   - `claude_binary.rs` uses discovery logic
   - Check Settings → Claude Version for detected path

### Version Mismatch
**Symptoms**:
- "Unsupported Claude version" warnings
- Missing features
- Incompatible flags

**Solutions**:
```bash
# Check installed version
claude --version

# Update Claude Code
npm update -g claude-code

# Or via Homebrew
brew upgrade claude-code
```

### Authentication Errors
**Symptoms**:
- "Not authenticated" errors
- API key issues
- Rate limiting

**Solutions**:
```bash
# Re-authenticate
claude auth

# Check auth status
claude auth status

# Check ~/.claude/ for credentials
ls -la ~/.claude/
```

### Project Detection Failures
**Symptoms**:
- "Could not determine project path" error
- Session not created in correct directory
- Project path decoding issues

**Causes**:
- Project path contains hyphens (bug in path encoding)
- JSONL file missing or corrupted
- CWD not set in session

**Solutions**:

1. **Known Issue**: Paths with hyphens may decode incorrectly
2. **Workaround**: Use `get_project_path_from_sessions()` instead of `decode_project_path()`
3. **Manual Fix**: Check JSONL file for correct `cwd` field

---

## Checkpoint & Timeline Errors

### Checkpoint Creation Failures
**Symptoms**:
- "Failed to create checkpoint" error
- Checkpoint directory missing
- Timeline not updating

**Causes**:
- Disk space full
- Permission denied on `~/.claude/checkpoints/`
- Compression failure
- File hash collision

**Solutions**:

1. **Check Disk Space**:
```bash
df -h ~/.claude/
```

2. **Check Permissions**:
```bash
ls -la ~/.claude/checkpoints/
chmod -R u+rw ~/.claude/checkpoints/
```

3. **Verify Checkpoint Structure**:
```bash
# Expected structure:
~/.claude/checkpoints/{project_id}/{session_id}/
  ├── timeline.json
  ├── checkpoints/
  │   └── {checkpoint_id}/
  │       ├── metadata.json
  │       └── messages.zst
  └── files/
      ├── content_pool/{hash}
      └── refs/{checkpoint_id}/{file}.json
```

### Checkpoint Restoration Failures
**Symptoms**:
- "Failed to restore checkpoint" error
- Files not restored correctly
- Corrupted project state

**Causes**:
- Missing checkpoint metadata
- Compression corruption
- File content missing from pool
- Timeline graph corruption

**Solutions**:

1. **Check Checkpoint Integrity**:
```bash
# List checkpoints
ls ~/.claude/checkpoints/{project_id}/{session_id}/checkpoints/

# Check specific checkpoint
cat ~/.claude/checkpoints/{project_id}/{session_id}/checkpoints/{id}/metadata.json
```

2. **Decompress Messages Manually**:
```bash
zstd -d messages.zst
```

3. **Recovery**:
- Use `list_checkpoints` to find valid checkpoints
- Restore from earlier checkpoint
- If all fail, restart session from JSONL

### Content Pool Corruption
**Symptoms**:
- "Content file missing for hash" warnings
- Files restored as empty
- Checkpoint size mismatch

**Causes**:
- Incomplete save operation
- Garbage collection removed active content
- Hash collision (extremely rare)

**Solutions**:

1. **Run Garbage Collection**:
```bash
# Via Tauri command: cleanup_old_checkpoints
# This also runs garbage_collect_content
```

2. **Manual Recovery**:
```bash
# Check content pool
ls ~/.claude/checkpoints/{project_id}/{session_id}/files/content_pool/

# Verify references
ls ~/.claude/checkpoints/{project_id}/{session_id}/files/refs/{checkpoint_id}/
```

---

## Agent Execution Failures

### Agent Won't Start
**Symptoms**:
- "Failed to execute agent" error
- Agent shows "pending" forever
- No process registered

**Causes**:
- Claude binary issues
- Invalid system prompt
- Model not available
- Hooks execution failure

**Solutions**:

1. **Check Agent Configuration**:
   - Verify system prompt is valid
   - Check model name (e.g., "claude-3-5-sonnet-20241022")
   - Review hooks configuration

2. **Test Directly**:
```bash
# Test Claude with agent's system prompt
claude --model claude-3-5-sonnet-20241022 --system-prompt "$(cat agent_prompt.txt)" -p "test"
```

3. **Check Logs**:
   - Look for "Failed to spawn Claude" errors
   - Check process registry errors

### Live Output Not Showing
**Symptoms**:
- Agent running but no output visible
- Output appears only after completion
- Partial output shown

**Causes**:
- ProcessRegistry buffer not flushing
- Frontend not polling output
- JSONL file write delay
- Event emission failure

**Solutions**:

1. **Check Output Source**:
   - Live output: `get_live_session_output` (from stdout buffer)
   - File output: `get_session_output` (from JSONL file)

2. **Polling Configuration**: Frontend should poll every 1-2 seconds

3. **Manual Output Check**:
```bash
# Check JSONL file directly
tail -f ~/.claude/projects/{project_id}/{session_id}.jsonl
```

### Agent Cancellation Not Working
**Symptoms**:
- Cancel button does nothing
- Process continues running
- UI stuck on "cancelling"

**Causes**:
- ProcessRegistry kill failure
- PID not found
- Process already exited
- Multi-level kill needed

**Solutions**:

1. **Check Process Status**:
```bash
# Find process
ps aux | grep claude | grep {session_id}

# Kill manually
kill -TERM {pid}
```

2. **Force Kill via Registry**:
   - Uses SIGTERM → wait → SIGKILL cascade
   - Check `process/registry.rs::kill_process` logic

3. **System Kill** (last resort):
```bash
pkill -f "claude.*{project_path}"
```

### Metrics Not Updating
**Symptoms**:
- Token count stuck at 0
- Duration not calculating
- Cost estimates missing

**Causes**:
- JSONL parsing failure
- Usage entries missing
- Real-time metrics not collected

**Solutions**:

1. **Check JSONL Format**: Verify usage entries present
2. **Refresh Metrics**: Use `get_agent_run_with_real_time_metrics`
3. **Manual Calculation**: Parse JSONL and sum tokens

---

## Performance & Resource Problems

### High Memory Usage
**Symptoms**:
- App using >1GB RAM
- System slowdown
- Memory leaks over time

**Causes**:
- Large JSONL files loaded into memory
- Session output accumulation
- React component memory leaks
- Checkpoint file caching

**Solutions**:

1. **Clear Old Sessions**:
```bash
# Check session file sizes
du -sh ~/.claude/projects/*/

# Archive old sessions
mkdir ~/.claude/archive/
mv ~/.claude/projects/{old_project} ~/.claude/archive/
```

2. **Limit Output Caching**:
   - Frontend output cache has size limit
   - Clear cache on session end

3. **Monitor Memory**:
```bash
# macOS
top -l 1 | grep opcode

# Check process memory
ps aux | grep opcode | awk '{print $4, $11}'
```

### Slow Session Loading
**Symptoms**:
- Session history takes >5s to load
- UI freezes when opening session
- Large JSONL files

**Causes**:
- Loading entire JSONL into memory
- No pagination
- Frontend rendering too many messages

**Solutions**:

1. **Pagination**: Load messages in chunks
2. **Virtual Scrolling**: Render only visible messages
3. **Message Limit**: Frontend should limit to last 1000 messages

### High CPU Usage
**Symptoms**:
- CPU constantly high (>50%)
- Fan running loudly
- Battery drain

**Causes**:
- Polling intervals too aggressive
- React re-renders
- Multiple Claude processes
- Infinite loops in event handlers

**Solutions**:

1. **Check Polling**:
   - Should be 1-2 second intervals
   - Disable when not active

2. **Profile React**:
   - Use React DevTools Profiler
   - Look for unnecessary renders

3. **Check Processes**:
```bash
ps aux | grep claude
# Should see only active sessions
```

---

## Web Server Mode Issues

### Cannot Access from Phone
**Symptoms**:
- Desktop can access `http://localhost:8080`
- Phone gets connection refused
- Timeout errors

**Causes**:
- Server binding to 127.0.0.1 instead of 0.0.0.0
- Firewall blocking port
- Phone not on same network
- Wrong IP address

**Solutions**:

1. **Check Server Binding**:
```rust
// In web_server.rs, should bind to:
SocketAddr::from(([0, 0, 0, 0], port))
// NOT: ([127, 0, 0, 1], port)
```

2. **Find Your IP**:
```bash
# macOS/Linux
ifconfig | grep "inet " | grep -v 127.0.0.1

# Use this IP on phone
http://192.168.x.x:8080
```

3. **Firewall**:
```bash
# macOS - allow incoming on port 8080
# Will prompt on first access

# Linux - allow port
sudo ufw allow 8080
```

### CORS Errors
**Symptoms**:
- "CORS policy" errors in browser console
- API calls failing from phone
- "Access-Control-Allow-Origin" errors

**Causes**:
- CORS layer misconfiguration
- Origin restrictions

**Solutions**:

Check `web_server.rs` CORS configuration:
```rust
let cors = CorsLayer::new()
    .allow_origin(Any)  // Should allow all origins
    .allow_methods([Method::GET, Method::POST, ...])
    .allow_headers(Any);
```

### WebSocket Issues (Web Mode)
**Symptoms**:
- Claude execution not working
- WebSocket connection fails
- "Connection closed unexpectedly"

**Known Issues** (from `web_server.design.md`):
- Process cancellation NOT IMPLEMENTED
- Cancel button does nothing
- stderr not captured
- Missing claude-cancelled events

**Solutions**:
1. **Use Desktop App** for reliable Claude execution
2. **Web Server**: Read-only mode recommended
3. **Workaround**: Refresh page to force cleanup

### HTTPS / WSS Issues
**Symptoms**:
- Secure WebSocket (wss://) connection fails
- Mixed content warnings
- Insecure connection errors

**Causes**:
- HTTP server but browser requires HTTPS
- Self-signed certificate issues

**Solutions**:

1. **Use HTTP** for local development:
   - `ws://` protocol
   - Disable secure context requirements

2. **HTTPS Setup** (production):
```bash
# Generate self-signed cert
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Configure Axum with TLS
# (requires additional implementation)
```

---

## Diagnostic Commands

### System Information
```bash
# Rust version
rustc --version
cargo --version

# Bun version
bun --version

# Claude version
claude --version

# Node version (if using NVM)
node --version
npm --version
```

### Check Running Processes
```bash
# All Opcode processes
ps aux | grep opcode

# Claude processes
ps aux | grep claude

# With details
lsof -c opcode
```

### Database Inspection
```bash
# Open database
sqlite3 ~/.local/opcode/agents.db

# List tables
.tables

# Check agents
SELECT id, name, model FROM agents;

# Check runs
SELECT id, agent_name, status, project_path FROM agent_runs ORDER BY created_at DESC LIMIT 10;

# Check settings
SELECT * FROM app_settings;
```

### File System Checks
```bash
# Check Claude directory
tree ~/.claude/ -L 3

# Session file sizes
find ~/.claude/projects -name "*.jsonl" -exec du -h {} \; | sort -h

# Checkpoint storage
du -sh ~/.claude/checkpoints/*/

# Log files
ls -lah /Users/max/local/opcode/src-tauri/target/*/opcode.log
```

### Network Diagnostics
```bash
# Check ports in use
lsof -i :8080
lsof -i :1420

# Test WebSocket (web mode)
websocat ws://localhost:8080/ws/claude

# HTTP test
curl http://localhost:8080/api/projects
```

---

## Emergency Recovery Procedures

### Complete Reset (NUCLEAR OPTION)
⚠️ **WARNING**: This will delete all data!

```bash
# 1. Backup everything
mkdir ~/opcode-backup
cp -r ~/.claude ~/opcode-backup/
cp -r ~/.local/opcode ~/opcode-backup/

# 2. Kill all processes
pkill -f opcode
pkill -f claude

# 3. Remove all data
rm -rf ~/.local/opcode/
rm -rf ~/.claude/checkpoints/
# Keep ~/.claude/projects/ for sessions

# 4. Restart application
# New database will be created
```

### Database Recovery
```bash
# 1. Backup
cp ~/.local/opcode/agents.db ~/.local/opcode/agents.db.backup

# 2. Export data
sqlite3 ~/.local/opcode/agents.db <<EOF
.mode insert
.output backup.sql
.dump
.exit
EOF

# 3. Create fresh database
rm ~/.local/opcode/agents.db

# 4. Restart app - new DB created

# 5. Re-import if needed
# (requires manual SQL editing)
```

### Session Recovery
```bash
# If session JSONL file corrupted:

# 1. Find session file
ls ~/.claude/projects/{project_id}/{session_id}.jsonl

# 2. Validate JSON lines
while read line; do
  echo "$line" | jq . > /dev/null || echo "Invalid JSON: $line"
done < session.jsonl

# 3. Extract valid lines
while read line; do
  echo "$line" | jq . > /dev/null && echo "$line"
done < session.jsonl > session_fixed.jsonl

# 4. Replace file
mv session_fixed.jsonl session.jsonl
```

### Reinstall (Keep Data)
```bash
# 1. Stop app
pkill -f opcode

# 2. Pull latest code
cd /Users/max/local/opcode
git pull

# 3. Rebuild
bun install
bun run build

# 4. Rebuild Tauri
cd src-tauri
cargo clean
cargo build

# 5. Restart
cd ..
bun run tauri dev
```

---

## Log Files & Debugging

### Log Locations

**Desktop App**:
```bash
# macOS
~/Library/Logs/com.opcode.dev/
/Users/max/local/opcode/src-tauri/target/debug/

# Linux
~/.local/share/opcode/logs/

# Windows
%APPDATA%\opcode\logs\
```

**Web Server**:
- stdout/stderr (terminal output)
- systemd journal (if running as service)

### Enable Debug Logging

**Rust Side**:
```bash
# Set log level
export RUST_LOG=debug

# Or for specific modules
export RUST_LOG=opcode::process=trace,opcode::commands=debug

# Run with logging
RUST_LOG=debug bun run tauri dev
```

**Frontend Side**:
```javascript
// Browser console
localStorage.setItem('debug', 'opcode:*');

// Or specific namespaces
localStorage.setItem('debug', 'opcode:api,opcode:events');
```

### Reading Logs

**Look for Common Patterns**:
```bash
# Errors
grep -i error opcode.log

# Process lifecycle
grep -i "spawn\|kill\|exit" opcode.log

# Database issues
grep -i "sqlite\|database\|locked" opcode.log

# Claude issues
grep -i "claude\|binary\|version" opcode.log
```

**Tauri Event Logs**:
```bash
# Event emissions
grep "emit" opcode.log

# Event listeners
grep "listen" opcode.log
```

### Performance Profiling

**Rust Profiling**:
```bash
# Install cargo-flamegraph
cargo install flamegraph

# Profile desktop app
cargo flamegraph --bin opcode

# Profile web server
cargo flamegraph --bin opcode-web
```

**Frontend Profiling**:
- Open Chrome DevTools
- Performance tab → Record → Stop
- Look for long tasks, layout thrashing

### Memory Debugging

```bash
# macOS - Instruments
# Xcode → Open Developer Tool → Instruments → Allocations

# Linux - valgrind
valgrind --leak-check=full ./target/debug/opcode

# Heap profiling
cargo install cargo-instruments
cargo instruments --template Allocations --bin opcode
```

---

## Additional Resources

### Code References
- Process management: `/Users/max/local/opcode/src-tauri/src/process/registry.rs`
- Claude integration: `/Users/max/local/opcode/src-tauri/src/commands/claude.rs`
- Binary detection: `/Users/max/local/opcode/src-tauri/src/claude_binary.rs`
- Web server: `/Users/max/local/opcode/src-tauri/src/web_server.rs`
- Error handling: `/Users/max/local/opcode/src/components/ErrorBoundary.tsx`

### Known Issues
- Web server session isolation: `web_server.design.md`
- Path decoding with hyphens: Fixed in `get_project_path_from_sessions()`
- Multiple concurrent sessions in web mode: Not supported

### Support
- GitHub Issues: (repository link)
- Documentation: `/Users/max/local/opcode/docs/`
- Project instructions: `CLAUDE.md`
