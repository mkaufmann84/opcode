# Setup Issues & Troubleshooting Guide

This comprehensive guide covers all known setup issues, their root causes, solutions, and prevention strategies for the opcode project.

## Table of Contents

- [Quick Reference](#quick-reference)
- [Environment Setup Issues](#environment-setup-issues)
- [Build & Compilation Issues](#build--compilation-issues)
- [Runtime Issues](#runtime-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Dependency Issues](#dependency-issues)
- [Advanced Troubleshooting](#advanced-troubleshooting)
- [Getting Help](#getting-help)

---

## Quick Reference

### Most Common Issues

1. **Cargo environment not loaded** - Run `source "$HOME/.cargo/env"`
2. **Missing frontend build** - Run `bun run build` before `tauri dev`
3. **Multiple binaries error** - Already fixed in Cargo.toml (default-run = "opcode")
4. **Claude binary not found** - Install Claude Code CLI and add to PATH

### Quick Diagnosis

```bash
# Check if all prerequisites are installed
which bun          # Should output: /path/to/bun
which cargo        # Should output: /path/to/cargo
which rustc        # Should output: /path/to/rustc
which claude       # Should output: /path/to/claude
node --version     # Optional, but useful
```

---

## Environment Setup Issues

### Issue 1: Cargo Environment Not Loaded

**Severity**: High
**Affects**: All platforms
**First Occurrence**: Initial setup

**Error Messages**:
```
failed to get cargo metadata: No such file or directory (os error 2)
```
```
cargo: command not found
```
```
rustc: command not found
```

**Root Cause**:
Rust installer adds cargo to `~/.cargo/env` but doesn't automatically update your shell's environment. The cargo binary directory (`~/.cargo/bin`) is not in your PATH.

**Immediate Fix**:
```bash
# Load cargo environment for current session
source "$HOME/.cargo/env"

# Verify it works
cargo --version
```

**Permanent Solution**:

For **Bash** (`~/.bashrc` or `~/.bash_profile`):
```bash
# Add this line to your shell config
source "$HOME/.cargo/env"
```

For **Zsh** (`~/.zshrc`):
```bash
# Add this line to your shell config
source "$HOME/.cargo/env"
```

For **Fish** (`~/.config/fish/config.fish`):
```fish
# Add this line to your shell config
source "$HOME/.cargo/env.fish"
```

**Apply Changes**:
```bash
# Option 1: Reload shell config
source ~/.zshrc  # or ~/.bashrc for bash

# Option 2: Restart shell
exec $SHELL

# Option 3: Close and reopen terminal
```

**Verification**:
```bash
# Should show cargo version without errors
cargo --version

# Should show path to cargo binary
which cargo
# Expected: /Users/username/.cargo/bin/cargo (macOS/Linux)
# Expected: C:\Users\username\.cargo\bin\cargo.exe (Windows)

# Verify PATH contains cargo
echo $PATH | grep -o "[^:]*cargo[^:]*"
```

**Prevention**:
- Always add cargo to shell profile during Rust installation
- Use `rustup` installer which handles this automatically
- Add verification step to your onboarding checklist

---

### Issue 2: Missing Frontend Build

**Severity**: High
**Affects**: All platforms
**First Occurrence**: First run, after frontend changes

**Error Messages**:
```
The `frontendDist` configuration is set to `"../dist"` but this path doesn't exist
```
```
Error: Could not find "../dist" directory
```
```
thread 'main' panicked at 'Failed to read dist directory'
```

**Root Cause**:
Opcode uses an unusual Tauri workflow where the frontend must be built BEFORE running `tauri dev`. The `beforeDevCommand` in `tauri.conf.json` is intentionally empty (`""`), so Tauri doesn't automatically build the frontend.

This is different from typical Tauri projects that run a dev server during development.

**Immediate Fix**:
```bash
# Build the frontend
bun run build

# Then run Tauri
bun run tauri dev
```

**One-Line Solution**:
```bash
# Build and run in one command
bun run build && bun run tauri dev
```

**Using Just** (recommended):
```bash
# Just handles the build automatically
just dev
# or
just quick
```

**Detailed Explanation**:

The build process:
1. `bun run build` compiles React/TypeScript frontend
2. Vite bundles everything into `dist/` folder
3. Tauri looks for `dist/` folder as specified in `tauri.conf.json`
4. If `dist/` doesn't exist, Tauri fails immediately

**Why This Workflow?**:
- Faster iteration during Rust development
- No hot-reload overhead during Tauri dev
- Explicit control over when frontend rebuilds
- Simpler configuration for web server mode

**When to Rebuild**:
- First time setup
- After pulling changes that modify frontend code
- After modifying any files in `src/` directory
- After changing dependencies in `package.json`
- When switching branches with frontend changes

**Verification**:
```bash
# Check if dist folder exists
ls dist/
# Should show: index.html, assets/, etc.

# Check dist folder size
du -sh dist/
# Should be several MB (not empty)

# Verify index.html exists
test -f dist/index.html && echo "Frontend built successfully"
```

**Prevention**:
- Use `just dev` which handles build automatically
- Add build step to your git hooks
- Document this in team onboarding
- Create shell alias: `alias opdev='bun run build && bun run tauri dev'`

**Related Configuration**:
```json
// tauri.conf.json
{
  "build": {
    "beforeDevCommand": "",  // Intentionally empty!
    "beforeBuildCommand": "bun run build",
    "frontendDist": "../dist"
  }
}
```

---

### Issue 3: Multiple Binaries Error (FIXED)

**Severity**: Medium (now fixed in repository)
**Affects**: All platforms
**Status**: Resolved in commit, should not occur with current code

**Error Messages**:
```
cargo run could not determine which binary to run
available binaries: opcode, opcode-web
```

**Root Cause**:
The project defines two binaries in `Cargo.toml`:
- `opcode` - Desktop GUI app (main)
- `opcode-web` - Web server for mobile access

Without `default-run`, cargo doesn't know which to execute.

**Current Fix** (already in Cargo.toml):
```toml
[package]
name = "opcode"
version = "0.2.1"
default-run = "opcode"  # This line fixes the issue

[[bin]]
name = "opcode"
path = "src/main.rs"

[[bin]]
name = "opcode-web"
path = "src/web_main.rs"
```

**If You Still Encounter This**:

Manual workaround:
```bash
# Run desktop app explicitly
cargo run --bin opcode

# Run web server explicitly
cargo run --bin opcode-web
```

Using Just:
```bash
# Run desktop app
just dev

# Run web server
just web
```

**Verification**:
```bash
# Check Cargo.toml has default-run
grep "default-run" src-tauri/Cargo.toml
# Expected output: default-run = "opcode"

# Test default run works
cd src-tauri && cargo run --help
# Should run opcode binary, not show binary selection error
```

**Why Two Binaries?**:
- `opcode`: Tauri desktop app with native OS integration
- `opcode-web`: Standalone web server for browser/mobile access
- Allows running on phones/tablets via browser
- Same Rust codebase, different execution modes

---

### Issue 4: Bun Not Found

**Severity**: High
**Affects**: All platforms
**First Occurrence**: Initial setup

**Error Messages**:
```
bun: command not found
```
```
npm ERR! missing script: build
```
```
Error: Cannot find module 'bun'
```

**Root Cause**:
Bun is not installed or not in PATH. This project requires Bun (not npm/yarn/pnpm) as its JavaScript package manager.

**Check Installation**:
```bash
# Check if bun is installed
which bun
# If no output, bun is not installed

# Check bun version
bun --version
# Should show version 1.3.0+
```

**Install Bun**:

**macOS/Linux**:
```bash
# Install bun
curl -fsSL https://bun.sh/install | bash

# Reload shell to update PATH
exec $SHELL

# Verify installation
bun --version
```

**Windows**:
```powershell
# Using PowerShell
powershell -c "irm bun.sh/install.ps1 | iex"

# Restart PowerShell

# Verify installation
bun --version
```

**Alternative (via npm)**:
```bash
# If you have npm installed
npm install -g bun

# Verify
bun --version
```

**Post-Installation**:
```bash
# Install project dependencies
cd /path/to/opcode
bun install

# Verify dependencies installed
ls node_modules/ | wc -l
# Should show 400+ packages
```

**PATH Issues**:

If `bun: command not found` persists after installation:

```bash
# Check where bun was installed
ls ~/.bun/bin/bun

# Add to PATH manually
echo 'export PATH="$HOME/.bun/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify
which bun
```

**Verification**:
```bash
# Complete verification
bun --version && echo "✓ Bun installed"
bun install && echo "✓ Dependencies installed"
bun run build && echo "✓ Build works"
```

**Why Bun?**:
- 10-20x faster than npm for installs
- Native TypeScript support
- Drop-in replacement for Node.js
- Better monorepo support
- Smaller disk footprint

---

### Issue 5: Claude Code CLI Not Found

**Severity**: Critical
**Affects**: All platforms
**First Occurrence**: Runtime, when executing Claude commands

**Error Messages**:
```
claude: command not found
```
```
Claude Code not found. Please ensure it's installed
```
```
Error: No valid Claude installation found
```
```
Failed to find claude binary in any location
```

**Root Cause**:
The Claude Code CLI is not installed, not in PATH, or installed in a non-standard location that opcode doesn't check.

**Check Installation**:
```bash
# Check if claude is accessible
which claude

# Check version
claude --version

# If not found, check common locations
ls /usr/local/bin/claude
ls /opt/homebrew/bin/claude
ls ~/.local/bin/claude
ls ~/.nvm/versions/node/*/bin/claude
```

**Install Claude Code**:

1. Visit [Claude Code official site](https://claude.ai/code)
2. Download installer for your platform
3. Follow installation instructions
4. Verify installation:

```bash
# Should show version
claude --version

# Should show help
claude --help
```

**PATH Configuration**:

If Claude is installed but not found:

```bash
# Find where claude is installed
find ~ -name "claude" -type f 2>/dev/null

# Add to PATH (adjust path as needed)
echo 'export PATH="/path/to/claude/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Verify
which claude
```

**Manual Path Setup in Opcode**:

If you can't add Claude to PATH, opcode will try to find it in:
- System PATH
- `/usr/local/bin/claude`
- `/opt/homebrew/bin/claude`
- `~/.nvm/versions/node/*/bin/claude`
- `~/.claude/local/claude`
- `~/.local/bin/claude`

**Custom Installation Location**:

For non-standard installations:

```bash
# Create symlink to standard location
sudo ln -s /your/custom/path/to/claude /usr/local/bin/claude

# Or add to PATH
export PATH="/your/custom/path/to:$PATH"
```

**Verification**:
```bash
# Full verification
claude --version
# Should show: Claude Code CLI v1.x.x

# Test basic command
echo "test" | claude --dangerously-skip-permissions

# Check opcode can find it (from project root)
bun run tauri dev
# Should start without "claude not found" errors
```

**Troubleshooting Detection**:

The detection logic is in `src-tauri/src/claude_binary.rs`. If opcode still can't find Claude:

```bash
# Enable debug logging
RUST_LOG=debug bun run tauri dev

# Look for these log lines:
# "Searching for claude binary..."
# "Found Claude installation: path=..."
# "Selected Claude installation: ..."
```

**Multiple Claude Versions**:

If you have multiple Claude installations:
- Opcode selects the highest version automatically
- Check which one is selected in debug logs
- You can force a specific version by setting it in the database (advanced)

---

## Build & Compilation Issues

### Issue 6: Rust Compilation Errors

**Severity**: Medium to High
**Affects**: All platforms
**Occurrence**: During build, after dependency updates

**Common Error Messages**:
```
error: could not compile `opcode`
```
```
error[E0425]: cannot find value `X` in this scope
```
```
linking with `cc` failed
```
```
error: failed to run custom build command for `X`
```

**Potential Causes & Solutions**:

#### A. Outdated Rust Version

```bash
# Check Rust version
rustc --version
# Should be 1.70.0 or later

# Update Rust
rustup update stable

# Set stable as default
rustup default stable

# Verify
rustc --version
```

#### B. Corrupted Build Cache

```bash
# Clean all build artifacts
cd src-tauri
cargo clean

# Remove target directory completely
rm -rf target/

# Rebuild from scratch
cd ..
bun run build
bun run tauri dev
```

#### C. Dependency Conflicts

```bash
# Update Cargo.lock
cd src-tauri
cargo update

# Or remove lock and regenerate
rm Cargo.lock
cargo build
```

#### D. Platform-Specific Linker Issues

**macOS**:
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Verify
xcode-select -p
# Should output: /Library/Developer/CommandLineTools
```

**Linux**:
```bash
# Install build essentials
sudo apt update
sudo apt install -y build-essential pkg-config
```

**Windows**:
```powershell
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Select "Desktop development with C++"
```

**Verification**:
```bash
# Test compilation
cd src-tauri
cargo check

# Full build test
cargo build

# If successful, run app
cd ..
bun run tauri dev
```

---

### Issue 7: Frontend TypeScript Errors

**Severity**: Medium
**Affects**: All platforms
**Occurrence**: During `bun run build`

**Error Messages**:
```
error TS2307: Cannot find module '@/...'
```
```
error TS2345: Argument of type 'X' is not assignable to parameter of type 'Y'
```
```
Type error: ... is not a valid JSX element
```

**Solutions**:

#### A. Missing Type Definitions

```bash
# Install missing types
bun add -d @types/node @types/react @types/react-dom

# Verify
ls node_modules/@types/
```

#### B. TypeScript Version Mismatch

```bash
# Check TypeScript version
bunx tsc --version
# Should match package.json version (~5.6.2)

# Reinstall if mismatch
bun remove typescript
bun add -d typescript@~5.6.2
```

#### C. Path Alias Issues

Check `tsconfig.json`:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]  // Must match vite.config.ts
    }
  }
}
```

Check `vite.config.ts`:
```typescript
resolve: {
  alias: {
    "@": fileURLToPath(new URL("./src", import.meta.url)),
  },
}
```

#### D. Stale Node Modules

```bash
# Clean and reinstall
rm -rf node_modules/
bun install

# Clear bun cache
bun pm cache rm

# Reinstall
bun install
```

**Verification**:
```bash
# Type check without emitting
bunx tsc --noEmit

# If successful
bun run build
```

---

### Issue 8: Out of Memory During Build

**Severity**: Medium
**Affects**: Systems with <4GB RAM
**Occurrence**: During cargo build or bun build

**Error Messages**:
```
fatal error: Killed (signal 9)
```
```
error: could not compile `X` (out of memory)
```
```
FATAL ERROR: Reached heap limit
```

**Solutions**:

#### A. Limit Parallel Cargo Jobs

```bash
# Build with fewer parallel jobs
cd src-tauri
cargo build -j 2

# Or set permanently
export CARGO_BUILD_JOBS=2
echo 'export CARGO_BUILD_JOBS=2' >> ~/.zshrc
```

#### B. Increase Swap Space (Linux)

```bash
# Check current swap
free -h

# Create 4GB swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

#### C. Use Release Mode with Optimizations

```bash
# Release build uses less memory
bun run tauri build --debug
# Smaller binary, faster compilation than full release
```

#### D. Close Other Applications

```bash
# Before building
# - Close browsers with many tabs
# - Close IDEs
# - Close Docker if running
# - Close other memory-intensive apps
```

**Verification**:
```bash
# Monitor memory during build
watch -n 1 free -h  # Linux
watch -n 1 vm_stat  # macOS

# Build with monitoring
cargo build
```

---

## Runtime Issues

### Issue 9: Application Won't Launch

**Severity**: High
**Affects**: All platforms
**Occurrence**: After build, when running executable

**Symptoms**:
- App window doesn't appear
- Process starts then immediately exits
- No error messages visible

**Diagnosis**:

```bash
# Run from terminal to see errors
./src-tauri/target/debug/opcode  # or release/opcode

# Check if process is running
ps aux | grep opcode

# Check system logs
# macOS:
log show --predicate 'process == "opcode"' --last 5m

# Linux:
journalctl -xe | grep opcode
```

**Common Causes**:

#### A. Missing dist/ Folder

```bash
# Verify dist exists
ls dist/

# If missing, rebuild frontend
bun run build
```

#### B. Wrong Working Directory

```bash
# Run from project root, not src-tauri
cd /path/to/opcode
./src-tauri/target/debug/opcode

# NOT from src-tauri directory
```

#### C. Port Already in Use (Dev Mode)

```bash
# Check if port 1420 is in use
lsof -i :1420  # macOS/Linux
netstat -ano | findstr :1420  # Windows

# Kill process using port
kill -9 <PID>
```

#### D. Database Corruption

```bash
# Check app data directory
ls ~/Library/Application\ Support/opcode/  # macOS
ls ~/.config/opcode/  # Linux
ls %APPDATA%/opcode/  # Windows

# Rename to backup (will create fresh DB)
mv ~/Library/Application\ Support/opcode{,.backup}
```

**Verification**:
```bash
# Successful launch should show:
# - Application window appears
# - No error popups
# - Can navigate UI

# Debug launch
RUST_LOG=debug ./src-tauri/target/debug/opcode
```

---

### Issue 10: WebSocket Connection Failures (Web Server Mode)

**Severity**: Medium
**Affects**: Web server mode (`opcode-web`)
**Occurrence**: When using browser/mobile access

**Error Messages** (in browser console):
```
WebSocket connection to 'ws://localhost:8080/ws/claude' failed
```
```
Failed to connect to WebSocket
```
```
Connection closed before session established
```

**Root Cause**:
Web server not running, firewall blocking, or CORS issues.

**Solutions**:

#### A. Start Web Server

```bash
# Start web server
just web

# Or manually
cd src-tauri
cargo run --bin opcode-web

# With custom port
cargo run --bin opcode-web -- --port 3000
```

#### B. Check Server is Running

```bash
# Test HTTP endpoint
curl http://localhost:8080/api/installations

# Should return JSON, not "Connection refused"
```

#### C. Firewall Configuration

**macOS**:
```bash
# Allow incoming connections
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/opcode-web
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblock /path/to/opcode-web
```

**Linux (ufw)**:
```bash
# Allow port 8080
sudo ufw allow 8080/tcp
sudo ufw reload
```

**Windows**:
```powershell
# Add firewall rule
New-NetFirewallRule -DisplayName "Opcode Web Server" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

#### D. CORS Issues

If accessing from different origin:

```bash
# The web server allows all origins for development
# Check browser console for CORS errors
# If issues persist, access from same origin
```

**Mobile Access Setup**:

```bash
# Find your PC's IP
just ip

# Or manually
ip route get 1.1.1.1 | grep -oP 'src \K\S+'  # Linux
ipconfig getifaddr en0  # macOS WiFi
ipconfig | findstr IPv4  # Windows

# Access from phone browser
http://YOUR_IP:8080
```

**Known Web Server Limitations**:

From `web_server.design.md`:
- Session-scoped events broken (sessions interfere)
- Process cancellation not implemented
- stderr not captured
- Single user/session only - NOT production ready

**Verification**:
```bash
# Test WebSocket connection
wscat -c ws://localhost:8080/ws/claude
# Should connect without errors

# Test from browser
# Open browser dev tools
# Navigate to http://localhost:8080
# Check Console and Network tabs
```

---

## Platform-Specific Issues

### Linux Issues

#### Issue 11: webkit2gtk Not Found

**Severity**: Critical
**Affects**: Linux only
**Occurrence**: During cargo build

**Error Messages**:
```
Package webkit2gtk-4.1 was not found in the pkg-config search path
```
```
error: failed to run custom build command for `webkit2gtk-sys`
```

**Solutions**:

**Ubuntu/Debian 22.04+**:
```bash
sudo apt update
sudo apt install -y \
  libwebkit2gtk-4.1-dev \
  libgtk-3-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev \
  patchelf \
  build-essential \
  curl \
  wget \
  file \
  libssl-dev \
  libxdo-dev \
  libsoup-3.0-dev \
  libjavascriptcoregtk-4.1-dev
```

**Ubuntu/Debian 20.04** (older):
```bash
# Use webkit2gtk 4.0 instead
sudo apt install -y \
  libwebkit2gtk-4.0-dev \
  libgtk-3-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev
```

**Fedora/RHEL**:
```bash
sudo dnf install -y \
  webkit2gtk4.1-devel \
  gtk3-devel \
  libappindicator-gtk3-devel \
  librsvg2-devel \
  openssl-devel
```

**Arch Linux**:
```bash
sudo pacman -S --needed \
  webkit2gtk-4.1 \
  gtk3 \
  libappindicator-gtk3 \
  librsvg \
  openssl
```

**Verification**:
```bash
# Check webkit2gtk is installed
pkg-config --modversion webkit2gtk-4.1
# Should show version number

# Test compilation
cd src-tauri
cargo check
```

---

#### Issue 12: AppImage Doesn't Run

**Severity**: Medium
**Affects**: Linux AppImage users
**Occurrence**: When running built .AppImage

**Error Messages**:
```
dlopen(): error loading libfuse.so.2
```
```
AppImages require FUSE to run
```

**Solutions**:

**Install FUSE**:

```bash
# Ubuntu/Debian
sudo apt install -y libfuse2

# Fedora
sudo dnf install -y fuse fuse-libs

# Arch
sudo pacman -S fuse2
```

**Alternative - Extract and Run**:
```bash
# Extract AppImage
./opcode.AppImage --appimage-extract

# Run extracted binary
./squashfs-root/AppRun
```

**Verification**:
```bash
# AppImage should run
./opcode.AppImage

# Check FUSE
ls -la /dev/fuse
# Should exist
```

---

### macOS Issues

#### Issue 13: "opcode" is Damaged and Can't Be Opened

**Severity**: High
**Affects**: macOS only
**Occurrence**: When running downloaded .app or .dmg

**Error Messages**:
```
"opcode" is damaged and can't be opened. You should move it to the Trash.
```
```
"opcode.app" cannot be opened because the developer cannot be verified
```

**Root Cause**:
macOS Gatekeeper quarantine attribute on downloaded files.

**Solutions**:

#### A. Remove Quarantine Attribute

```bash
# For .app
xattr -cr /Applications/opcode.app

# For .dmg (before opening)
xattr -cr ~/Downloads/opcode.dmg
```

#### B. Allow in System Settings

1. Try to open app (will fail)
2. Go to **System Settings > Privacy & Security**
3. Scroll to **Security** section
4. Click **"Open Anyway"** next to opcode message
5. Confirm in dialog

#### C. Bypass Gatekeeper (Development)

```bash
# Disable gatekeeper check for this app
spctl --add /Applications/opcode.app

# Or globally (not recommended)
sudo spctl --master-disable
```

**Verification**:
```bash
# Check app signature
codesign -dvv /Applications/opcode.app

# Check quarantine attribute removed
xattr -l /Applications/opcode.app
# Should not show com.apple.quarantine
```

---

#### Issue 14: Xcode Command Line Tools Missing

**Severity**: High
**Affects**: macOS only
**Occurrence**: During build

**Error Messages**:
```
xcrun: error: invalid active developer path
```
```
error: linker `cc` not found
```
```
clang: error: no such file or directory: '/usr/include'
```

**Solutions**:

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Follow popup to complete installation

# Verify installation
xcode-select -p
# Should output: /Library/Developer/CommandLineTools

# Accept license if prompted
sudo xcodebuild -license accept

# Verify compiler
clang --version
# Should show Apple clang version
```

**If Installation Fails**:

```bash
# Download manually from Apple Developer
# https://developer.apple.com/download/more/
# Search for "Command Line Tools for Xcode"

# Or reset xcode-select
sudo rm -rf /Library/Developer/CommandLineTools
xcode-select --install
```

**Verification**:
```bash
# All should work
which clang
which cc
which ld

# Test compilation
echo 'int main() { return 0; }' > test.c
clang test.c -o test
./test && echo "Compiler works"
rm test test.c
```

---

### Windows Issues

#### Issue 15: MSVC Build Tools Not Found

**Severity**: Critical
**Affects**: Windows only
**Occurrence**: During cargo build

**Error Messages**:
```
error: linker `link.exe` not found
```
```
note: program not found
```
```
error: could not find native static library `msvcrt`
```

**Solutions**:

#### A. Install Visual Studio Build Tools

1. Download from [Visual Studio Downloads](https://visualstudio.microsoft.com/downloads/)
2. Select **"Build Tools for Visual Studio 2022"**
3. In installer, select:
   - **Desktop development with C++**
   - **Windows 10/11 SDK**
   - **MSVC v143 build tools**
4. Install (requires ~6GB space)
5. Restart computer

#### B. Alternative - Visual Studio Community

1. Install Visual Studio Community (free)
2. During installation, select:
   - **Desktop development with C++**
3. Complete installation
4. Restart computer

**Verification**:
```powershell
# Check if link.exe exists
where link.exe
# Should show path in Program Files\Microsoft Visual Studio\...

# Check MSVC environment
"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x64

# Test Rust build
cd src-tauri
cargo check
```

---

#### Issue 16: WebView2 Runtime Missing

**Severity**: High
**Affects**: Windows only
**Occurrence**: When running built .exe

**Error Messages**:
```
Error: WebView2 Runtime is not installed
```
```
Failed to create WebView
```

**Root Cause**:
Tauri on Windows requires WebView2 Runtime (included in Windows 11, but not always in Windows 10).

**Check Installation**:
```powershell
# Check registry for WebView2
Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
```

**Solutions**:

#### A. Install WebView2 Runtime

1. Download from [Microsoft WebView2](https://developer.microsoft.com/microsoft-edge/webview2/)
2. Download **"Evergreen Bootstrapper"**
3. Run installer
4. Restart application

#### B. Install via Chocolatey

```powershell
choco install webview2-runtime
```

#### C. Install via Winget

```powershell
winget install Microsoft.EdgeWebView2Runtime
```

**Verification**:
```powershell
# Check version
Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" | Select-Object pv
# Should show version number

# Test app
.\src-tauri\target\release\opcode.exe
```

---

## Dependency Issues

### Issue 17: Dependency Version Conflicts

**Severity**: Medium
**Affects**: All platforms
**Occurrence**: After dependency updates, bun install

**Error Messages**:
```
error: failed to select a version for `X`
```
```
WARN conflicting dependencies for package "Y"
```
```
error: package `Z` requires Rust version 1.XX.0
```

**Solutions**:

#### A. Update Bun Lock File

```bash
# Remove lock file
rm bun.lockb

# Reinstall
bun install

# Or update specific package
bun update <package-name>
```

#### B. Update Cargo Lock File

```bash
cd src-tauri

# Remove lock file
rm Cargo.lock

# Rebuild
cargo build

# Or update specific crate
cargo update -p <crate-name>
```

#### C. Check Rust Version Requirements

```bash
# Check current Rust version
rustc --version

# Update Rust
rustup update stable

# Check Cargo.toml for version requirements
grep "rust-version" src-tauri/Cargo.toml
```

#### D. Resolve Specific Conflicts

```bash
# Check dependency tree
bun pm ls <package-name>

# For Rust
cargo tree -p <crate-name>

# Find duplicate versions
cargo tree -d
```

**Verification**:
```bash
# Clean build test
rm -rf node_modules bun.lockb
bun install
bun run build

cd src-tauri
cargo clean
cargo build
```

---

### Issue 18: Image Crate Edition 2024 Error

**Severity**: Low
**Affects**: All platforms
**Status**: Fixed in Cargo.toml

**Error Messages**:
```
error: package `image v0.25.5` cannot be built because it requires rustc 1.XX.0 or newer, while the currently active rustc version is 1.YY.0
```
```
error: edition2024 is unstable
```

**Root Cause**:
Newer versions of the `image` crate require Rust edition 2024, which is not stable yet.

**Current Fix** (already in Cargo.toml):
```toml
[dependencies]
# Pin image to avoid edition2024 requirement
image = "=0.25.1"
```

**If You Encounter This**:

```bash
# Check Cargo.toml has pinned version
grep "image" src-tauri/Cargo.toml
# Should show: image = "=0.25.1"

# If not, add it
echo 'image = "=0.25.1"' >> src-tauri/Cargo.toml

# Update dependencies
cd src-tauri
cargo update
```

**Verification**:
```bash
# Check resolved version
cargo tree | grep "^image"
# Should show: image v0.25.1

# Build test
cargo check
```

---

## Advanced Troubleshooting

### Issue 19: Rust Warnings During Compilation

**Severity**: Low
**Affects**: All platforms
**Impact**: No functional issues, but clutters output

**Warning Messages**:
```
warning: unused variable: `X`
```
```
warning: function `Y` is never used
```
```
warning: method `register_sidecar_process` is never used
```
```
warning: variable does not need to be mutable
```

**Root Cause**:
Development code with unused variables, dead code paths, or inconsistent naming conventions.

**Known Warnings** (non-critical):
- `non_snake_case` in `web_server.rs:236` and `:244`
- `dead_code` for unused `register_sidecar_process` method
- Various unused imports during development

**To Suppress Warnings**:

```bash
# Build without warnings
cd src-tauri
cargo build 2>&1 | grep -v "warning:"

# Or allow specific warnings in code
# Add to top of file:
#![allow(dead_code)]
#![allow(unused_variables)]
```

**To Fix Warnings**:

```bash
# Auto-fix some warnings
cargo fix --allow-dirty

# Format code
cargo fmt

# Run clippy for suggestions
cargo clippy
```

**Verification**:
```bash
# Build and count warnings
cargo build 2>&1 | grep "warning:" | wc -l

# Check specific file
cargo check --message-format=json | jq 'select(.message.spans[0].file_name == "src/web_server.rs")'
```

---

### Issue 20: Hot Reload Not Working

**Severity**: Low
**Affects**: All platforms
**Expected Behavior**: This is intentional, not a bug

**Misconception**:
"Why doesn't the frontend auto-reload when I change files?"

**Root Cause**:
Opcode uses an unusual Tauri workflow:
- `beforeDevCommand` is empty in `tauri.conf.json`
- Frontend must be manually rebuilt
- No hot-reload/HMR during development
- This is intentional for faster Rust iteration

**Workflow**:

For **frontend changes**:
```bash
# Rebuild frontend
bun run build

# Tauri dev server will auto-reload
# (if still running)
```

For **Rust changes**:
```bash
# Rust changes auto-recompile
# Just save the file
# Tauri watches src-tauri/ automatically
```

**Why This Design?**:
- Faster Rust development without Vite overhead
- Simpler configuration for dual-mode (desktop/web)
- Explicit control over frontend rebuilds
- Reduces resource usage during development

**Alternative - Traditional Hot Reload**:

If you want hot reload, modify `tauri.conf.json`:

```json
{
  "build": {
    "beforeDevCommand": "bun run dev",  // Change this
    "frontendDist": "../dist"
  }
}
```

Then:
```bash
# This will now run Vite dev server
bun run tauri dev

# Frontend changes auto-reload
# But uses more resources
```

**Recommended Workflow**:

```bash
# Terminal 1 - Run Tauri (watches Rust)
bun run tauri dev

# Terminal 2 - Rebuild frontend as needed
bun run build
# Or set up watch mode:
bun run dev --watch
```

---

### Issue 21: Database Locked Errors

**Severity**: Medium
**Affects**: All platforms
**Occurrence**: During concurrent operations

**Error Messages**:
```
SqliteFailure(Error { code: DatabaseLocked, extended_code: 5 })
```
```
Error: database is locked
```
```
SQLITE_BUSY: database is locked
```

**Root Cause**:
Multiple processes or threads trying to write to SQLite database simultaneously.

**Solutions**:

#### A. Close Other Opcode Instances

```bash
# Check running instances
ps aux | grep opcode

# Kill extra instances
killall opcode  # macOS/Linux
taskkill /IM opcode.exe /F  # Windows
```

#### B. Reset Database Locks

```bash
# Find database location
# macOS
ls ~/Library/Application\ Support/opcode/*.db

# Linux
ls ~/.local/share/opcode/*.db

# Windows
dir %APPDATA%\opcode\*.db

# Check for lock files
ls ~/Library/Application\ Support/opcode/*.db-shm
ls ~/Library/Application\ Support/opcode/*.db-wal

# Remove if stale (with app closed)
rm ~/Library/Application\ Support/opcode/*.db-shm
rm ~/Library/Application\ Support/opcode/*.db-wal
```

#### C. Increase SQLite Timeout

In code (`src-tauri/src/...`), SQLite connections should have:
```rust
connection.busy_timeout(Duration::from_secs(5))?;
```

**Verification**:
```bash
# Ensure only one instance
ps aux | grep opcode | grep -v grep | wc -l
# Should show: 1

# Check database is not corrupted
sqlite3 ~/Library/Application\ Support/opcode/agents.db "PRAGMA integrity_check;"
# Should show: ok
```

---

### Issue 22: Permission Denied Errors

**Severity**: Medium
**Affects**: All platforms
**Occurrence**: File operations, project scanning

**Error Messages**:
```
Permission denied (os error 13)
```
```
Error: EACCES: permission denied
```
```
cannot access '/path/to/file': Permission denied
```

**Solutions**:

#### A. File System Permissions

**macOS**:
```bash
# Grant Full Disk Access
1. Open System Settings
2. Privacy & Security > Full Disk Access
3. Add opcode.app
4. Restart application
```

**Linux**:
```bash
# Fix file permissions
chmod +x src-tauri/target/release/opcode

# Fix directory permissions
chmod -R u+rwX ~/.claude/
```

**Windows**:
```powershell
# Run as Administrator
Right-click opcode.exe > Run as administrator
```

#### B. Claude Directory Permissions

```bash
# Ensure ~/.claude is writable
ls -la ~/.claude/

# Fix ownership
chown -R $USER ~/.claude/

# Fix permissions
chmod -R u+rwX ~/.claude/
```

#### C. Project Directory Access

```bash
# Ensure project directory is readable
chmod -R u+rX /path/to/your/project/

# Check if in restricted location
# Avoid running projects from:
# - System directories (/usr, /etc, etc.)
# - Protected locations (~/Library/Application Support)
```

**Verification**:
```bash
# Test read access
cat /path/to/file

# Test write access
touch /path/to/directory/test.txt && rm /path/to/directory/test.txt

# Check opcode can access
RUST_LOG=debug ./opcode
# Look for permission errors in logs
```

---

## Performance Issues

### Issue 23: Slow Build Times

**Severity**: Low
**Affects**: All platforms
**Impact**: Developer experience

**Symptoms**:
- Cargo build takes >5 minutes
- Bun install takes >2 minutes
- Full rebuild takes >10 minutes

**Solutions**:

#### A. Use Cargo Build Cache

```bash
# Install sccache (shared compilation cache)
cargo install sccache

# Configure cargo to use it
export RUSTC_WRAPPER=sccache

# Add to shell profile
echo 'export RUSTC_WRAPPER=sccache' >> ~/.zshrc
```

#### B. Parallel Compilation

```bash
# Use more CPU cores (default is # of cores)
export CARGO_BUILD_JOBS=8

# Or limit if memory constrained
export CARGO_BUILD_JOBS=4
```

#### C. Incremental Compilation

Already enabled by default, but verify:

```toml
# In src-tauri/.cargo/config.toml (create if missing)
[build]
incremental = true
```

#### D. Link-Time Optimization (Production Only)

Disable for faster debug builds:

```toml
# src-tauri/Cargo.toml
[profile.dev]
lto = false

[profile.release]
lto = true  # Keep for production
```

**Verification**:
```bash
# Measure build time
time cargo build

# First build: ~19s (downloading crates)
# Subsequent: ~1-2s (cached)

# Check cache hit rate (if using sccache)
sccache --show-stats
```

---

## Diagnostic Commands

### Quick Health Check

Run these commands to verify system setup:

```bash
#!/bin/bash
echo "=== Opcode Environment Check ==="

# Check Rust
echo -n "Rust: "
rustc --version || echo "❌ NOT INSTALLED"

# Check Cargo
echo -n "Cargo: "
cargo --version || echo "❌ NOT INSTALLED"

# Check Bun
echo -n "Bun: "
bun --version || echo "❌ NOT INSTALLED"

# Check Claude
echo -n "Claude: "
claude --version || echo "❌ NOT INSTALLED"

# Check Node (optional)
echo -n "Node: "
node --version || echo "⚠️  Optional"

# Check Git
echo -n "Git: "
git --version || echo "❌ NOT INSTALLED"

# Platform-specific checks
case "$(uname -s)" in
  Darwin)
    echo -n "Xcode CLI Tools: "
    xcode-select -p >/dev/null 2>&1 && echo "✓ Installed" || echo "❌ NOT INSTALLED"
    ;;
  Linux)
    echo -n "Build essentials: "
    dpkg -l | grep -q build-essential && echo "✓ Installed" || echo "❌ NOT INSTALLED"
    echo -n "webkit2gtk: "
    pkg-config --exists webkit2gtk-4.1 && echo "✓ Installed" || echo "❌ NOT INSTALLED"
    ;;
  MINGW*|MSYS*|CYGWIN*)
    echo "Windows detected"
    ;;
esac

# Check project files
echo -n "dist/ folder: "
[ -d "dist" ] && echo "✓ Exists" || echo "❌ Missing (run: bun run build)"

echo -n "node_modules/: "
[ -d "node_modules" ] && echo "✓ Exists" || echo "❌ Missing (run: bun install)"

echo -n "Cargo.toml: "
[ -f "src-tauri/Cargo.toml" ] && echo "✓ Exists" || echo "❌ Missing"

echo "=== End Check ==="
```

Save as `check-env.sh`, make executable, and run:
```bash
chmod +x check-env.sh
./check-env.sh
```

---

## Prevention Strategies

### Best Practices to Avoid Issues

1. **Always source cargo env**:
   ```bash
   # Add to ~/.zshrc or ~/.bashrc
   source "$HOME/.cargo/env"
   ```

2. **Use Just for consistency**:
   ```bash
   # Instead of manual commands
   just dev     # Handles build automatically
   just web     # Runs web server
   just clean   # Cleans all artifacts
   ```

3. **Keep dependencies updated**:
   ```bash
   # Weekly maintenance
   rustup update
   bun update
   cargo update
   ```

4. **Clean builds periodically**:
   ```bash
   # Monthly or after major changes
   just clean
   just rebuild
   ```

5. **Document custom setups**:
   - Non-standard Claude installation paths
   - Custom environment variables
   - Platform-specific quirks

6. **Use version managers**:
   ```bash
   # For Node/Bun versions
   # For Rust versions: rustup
   ```

---

## Getting Help

### Before Asking for Help

1. **Search existing issues**:
   - [GitHub Issues](https://github.com/getAsterisk/opcode/issues)
   - Check closed issues too

2. **Enable debug logging**:
   ```bash
   RUST_LOG=debug bun run tauri dev > debug.log 2>&1
   ```

3. **Gather system information**:
   ```bash
   # Run diagnostic script
   ./check-env.sh > system-info.txt

   # Include in report
   ```

4. **Create minimal reproduction**:
   - Fresh clone of repository
   - Clean environment (no customizations)
   - Step-by-step reproduction

### When to Ask for Help

- After trying all relevant solutions in this guide
- When errors persist after clean rebuild
- When encountering undocumented errors
- When platform-specific issues arise

### Where to Get Help

1. **GitHub Issues** (preferred):
   - [Report Bug](https://github.com/getAsterisk/opcode/issues)
   - Use issue template
   - Include debug logs

2. **Discord**:
   - [Join Discord](https://discord.com/invite/KYwhHVzUsY)
   - #support channel
   - Real-time help

3. **Discussions**:
   - [GitHub Discussions](https://github.com/getAsterisk/opcode/discussions)
   - For questions and general help

### Information to Include

When reporting issues:

```
**Environment**:
- OS: macOS 14.4 / Ubuntu 22.04 / Windows 11
- Rust: 1.90.0
- Bun: 1.3.0
- Claude Code: 1.0.41
- Opcode: 0.2.1

**Steps to Reproduce**:
1. ...
2. ...
3. ...

**Expected Behavior**:
...

**Actual Behavior**:
...

**Logs**:
```
[Paste debug logs here]
```

**Screenshots** (if applicable):
[Attach screenshots]
```

---

## Summary of All Documented Issues

| # | Issue | Severity | Platform | Status |
|---|-------|----------|----------|--------|
| 1 | Cargo environment not loaded | High | All | Documented |
| 2 | Missing frontend build | High | All | Documented |
| 3 | Multiple binaries error | Medium | All | Fixed in code |
| 4 | Bun not found | High | All | Documented |
| 5 | Claude Code CLI not found | Critical | All | Documented |
| 6 | Rust compilation errors | Medium-High | All | Documented |
| 7 | Frontend TypeScript errors | Medium | All | Documented |
| 8 | Out of memory during build | Medium | Low-RAM systems | Documented |
| 9 | Application won't launch | High | All | Documented |
| 10 | WebSocket connection failures | Medium | Web mode | Documented |
| 11 | webkit2gtk not found | Critical | Linux | Documented |
| 12 | AppImage doesn't run | Medium | Linux | Documented |
| 13 | macOS Gatekeeper quarantine | High | macOS | Documented |
| 14 | Xcode Command Line Tools missing | High | macOS | Documented |
| 15 | MSVC Build Tools not found | Critical | Windows | Documented |
| 16 | WebView2 Runtime missing | High | Windows | Documented |
| 17 | Dependency version conflicts | Medium | All | Documented |
| 18 | Image crate edition 2024 error | Low | All | Fixed in code |
| 19 | Rust warnings during compilation | Low | All | Documented |
| 20 | Hot reload not working | Low | All | By design |
| 21 | Database locked errors | Medium | All | Documented |
| 22 | Permission denied errors | Medium | All | Documented |
| 23 | Slow build times | Low | All | Documented |

**Total Issues Documented**: 23
**Critical Issues**: 3
**High Severity**: 8
**Medium Severity**: 9
**Low Severity**: 3

**Platform Coverage**:
- Linux-specific: 2 issues
- macOS-specific: 2 issues
- Windows-specific: 2 issues
- Cross-platform: 17 issues

---

## Version History

- **v1.0** (2025-10-20): Initial comprehensive guide
  - Documented 23 common setup issues
  - Added platform-specific sections
  - Included diagnostic commands
  - Added prevention strategies

---

**This guide is maintained as part of the opcode project documentation. For updates or corrections, please submit a PR or open an issue.**
