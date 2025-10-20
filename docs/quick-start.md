# Quick Start Guide

Complete guide to get opcode up and running on your machine from scratch.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation Steps](#installation-steps)
3. [First-Time Setup](#first-time-setup)
4. [Running the Application](#running-the-application)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)
7. [Next Steps](#next-steps)

---

## Prerequisites

Before installing opcode, ensure you have the following installed on your system.

### Required Software

#### 1. Claude Code CLI (Required)
The Claude Code CLI must be installed and available in your PATH.

**Installation:**
- Download from: [https://claude.ai/code](https://claude.ai/code)
- Follow the official installation instructions
- Verify installation:
  ```bash
  claude --version
  ```

**Note:** opcode is a GUI wrapper for Claude Code and requires the CLI to function.

#### 2. Bun (Required)
JavaScript runtime and package manager (version 1.0.0 or later recommended)

**Installation:**
```bash
# macOS, Linux, and WSL
curl -fsSL https://bun.sh/install | bash

# After installation, restart your terminal or run:
exec $SHELL
```

**Verify installation:**
```bash
bun --version
# Should show version 1.0.0 or later
```

**Install Location:** `~/.bun/bin/bun`

#### 3. Rust (Required)
Rust toolchain version 1.70.0 or later for building the Tauri backend

**Installation:**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Select default installation option (1)
```

**After installation, load Rust environment:**
```bash
source "$HOME/.cargo/env"
```

**Verify installation:**
```bash
rustc --version
# Should show version 1.70.0 or later

cargo --version
```

**Install Location:** `~/.cargo/bin/`

**Important:** Add Cargo to your shell profile to avoid having to source it every time:

For **bash** (`~/.bashrc`):
```bash
echo 'source "$HOME/.cargo/env"' >> ~/.bashrc
```

For **zsh** (`~/.zshrc`):
```bash
echo 'source "$HOME/.cargo/env"' >> ~/.zshrc
```

Then restart your terminal or run `exec $SHELL`.

#### 4. Git (Usually Pre-installed)
Required for cloning the repository.

**Verify installation:**
```bash
git --version
```

**Installation (if needed):**
- **macOS:** `brew install git` or install Xcode Command Line Tools: `xcode-select --install`
- **Ubuntu/Debian:** `sudo apt install git`
- **Windows:** Download from [https://git-scm.com](https://git-scm.com)

### Platform-Specific Dependencies

#### macOS
```bash
# Install Xcode Command Line Tools (if not already installed)
xcode-select --install

# Optional: Install pkg-config via Homebrew
brew install pkg-config
```

**Minimum macOS Version:** 10.15 (Catalina) or later

#### Linux (Ubuntu/Debian)
```bash
# Install system dependencies for Tauri
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

**Note:** On older Ubuntu versions, you may need `libwebkit2gtk-4.0-dev` instead.

#### Windows
- Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
  - Select "Desktop development with C++" workload during installation
- Install [WebView2](https://developer.microsoft.com/microsoft-edge/webview2/)
  - Usually pre-installed on Windows 11
  - Required for Windows 10

**Minimum Windows Version:** Windows 10 or later

### System Requirements

- **Operating System:** Windows 10/11, macOS 11+, or Linux (Ubuntu 20.04+)
- **RAM:** Minimum 4GB (8GB recommended for faster builds)
- **Storage:** At least 1GB free space (for dependencies and build artifacts)
- **Network:** Internet connection required for initial setup

---

## Installation Steps

Follow these steps in order for a successful installation.

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/getAsterisk/opcode.git

# Navigate to the project directory
cd opcode
```

### Step 2: Install Frontend Dependencies

```bash
# Install all JavaScript/TypeScript dependencies
bun install
```

**Expected output:** Installation of ~400+ packages (takes ~5-15 seconds depending on your internet speed)

**What this does:**
- Installs React, TypeScript, Vite, and all UI dependencies
- Installs Tauri CLI tools
- Sets up development tooling

### Step 3: Build the Frontend

**Important:** opcode uses an unusual Tauri workflow where you must build the frontend BEFORE running the app.

```bash
bun run build
```

**Expected output:**
- TypeScript compilation
- Vite build process
- Creates `dist/` directory with compiled frontend assets
- Build time: ~3-7 seconds

**What this creates:**
- `dist/` folder containing the React application bundle
- This folder is required by Tauri to run the app

### Step 4: Verify Cargo Environment

Before running the app, ensure Rust's Cargo is in your PATH:

```bash
# Test if cargo is available
cargo --version
```

**If you see "command not found":**
```bash
# Temporarily load cargo (this session only)
source "$HOME/.cargo/env"

# OR permanently add to your shell profile (recommended)
# For bash:
echo 'source "$HOME/.cargo/env"' >> ~/.bashrc && exec bash

# For zsh:
echo 'source "$HOME/.cargo/env"' >> ~/.zshrc && exec zsh
```

---

## First-Time Setup

### Understanding the Build Process

opcode has **two separate binaries** defined in `src-tauri/Cargo.toml`:
1. **opcode** - The main desktop GUI application (default)
2. **opcode-web** - Web server for browser/mobile access

The first time you run the app, Rust will:
- Download ~600 crates (Rust dependencies)
- Compile the entire Tauri backend
- Generate ~650 build artifacts
- **First compilation time: ~15-30 seconds** (depending on your CPU)

Subsequent runs will be much faster (~1-3 seconds) due to caching.

### Important Configuration Note

The project uses a special configuration:
- `beforeDevCommand` in `tauri.conf.json` is intentionally **empty**
- This means the frontend is NOT auto-built when running `tauri dev`
- You must manually run `bun run build` whenever you change frontend code
- This is **by design** for this project

---

## Running the Application

You have three methods to run opcode:

### Method 1: Using Bun (Recommended for Beginners)

```bash
# Make sure frontend is built
bun run build

# Start the desktop app
bun run tauri dev
```

**What happens:**
- First run: Downloads and compiles Rust dependencies (~15-30 seconds)
- Subsequent runs: Quick startup (~1-3 seconds)
- Opens the opcode desktop application window

**If you get "cargo not found":**
```bash
source "$HOME/.cargo/env" && bun run tauri dev
```

### Method 2: Using Just (Alternative Build Tool)

If you prefer using the `just` command runner:

```bash
# Quick start (builds frontend + runs app)
just dev

# Alternative (same as above)
just quick

# Run web server mode (for mobile/browser access)
just web

# Web server on custom port
just web-port 3000

# Get your local IP for phone access
just ip
```

**Install Just (if not already installed):**
```bash
# macOS
brew install just

# Linux
cargo install just

# Or download from: https://github.com/casey/just
```

### Method 3: Using Cargo Directly (Advanced)

```bash
# Build frontend first
bun run build

# Run desktop app
cd src-tauri && cargo run

# Or run from project root with explicit binary
cd src-tauri && cargo run --bin opcode

# Run web server mode
cd src-tauri && cargo run --bin opcode-web
```

### Running Web Server Mode

To access opcode from a mobile device or browser:

```bash
# Build frontend
bun run build

# Run web server (default port 8080)
just web

# OR with custom port
just web-port 3000

# Get your local IP address
just ip
```

Then access from your phone/browser at: `http://YOUR_LOCAL_IP:8080`

**Warning:** Web server mode has [known issues](web-server-notes.md) and is **single-user, single-session only**. Not recommended for production use.

---

## Verification

After running the app, verify everything is working correctly:

### 1. Application Window Opens
- The opcode window should appear
- Window is transparent/frameless by default
- Default size: 800x600 pixels

### 2. Check Console Output
Look for successful startup messages in your terminal:

```bash
# You should see something like:
    Finished `dev` profile [unoptimized + debuginfo] target(s) in X.XXs
     Running `target/debug/opcode`
```

**No errors** means successful startup.

### 3. Application Functionality
- Welcome screen appears with options for "CC Agents" or "Projects"
- Can navigate to Projects view
- Should detect `~/.claude/projects/` directory (if it exists)
- Can view Claude Code sessions (if any exist)

### 4. Claude Code Integration
Verify Claude Code is accessible:

```bash
# Open a new terminal and test
claude --version

# Check if claude data directory exists
ls ~/.claude
```

If `~/.claude` doesn't exist, it will be created when you first use Claude Code.

### 5. Verify Build Artifacts

Check that all necessary files were created:

```bash
# Frontend build artifacts
ls dist/
# Should show: index.html, assets/, etc.

# Rust build artifacts
ls src-tauri/target/debug/
# Should show: opcode and opcode-web executables
```

---

## Troubleshooting

### Common First-Run Issues

#### Issue 1: "cargo not found"

**Error:**
```
failed to get cargo metadata: No such file or directory (os error 2)
```

**Solution:**
```bash
# Temporary fix (this session only)
source "$HOME/.cargo/env"

# Run the app again
bun run tauri dev

# Permanent fix (add to shell profile)
echo 'source "$HOME/.cargo/env"' >> ~/.zshrc  # or ~/.bashrc
exec $SHELL
```

#### Issue 2: "bun not found"

**Error:**
```bash
bun: command not found
```

**Solution:**
```bash
# Restart your terminal
exec $SHELL

# Or manually add to PATH
export PATH="$HOME/.bun/bin:$PATH"

# Verify
bun --version
```

#### Issue 3: "frontendDist doesn't exist"

**Error:**
```
The `frontendDist` configuration is set to `"../dist"` but this path doesn't exist
```

**Solution:**
```bash
# Build the frontend first
bun run build

# Then run the app
bun run tauri dev
```

This is the most common issue for first-time users. **Always build frontend first!**

#### Issue 4: "multiple binaries" error

**Error:**
```
cargo run could not determine which binary to run
available binaries: opcode, opcode-web
```

**Solution:**
This should not happen as `default-run = "opcode"` is already set in `Cargo.toml`. If you see this:

```bash
# Explicitly specify the binary
cd src-tauri && cargo run --bin opcode
```

#### Issue 5: "claude command not found"

**Error:**
opcode starts but can't find Claude Code CLI.

**Solution:**
```bash
# Install Claude Code CLI from https://claude.ai/code
# Then verify installation
claude --version

# Check PATH
echo $PATH | grep -o '[^:]*claude[^:]*'
```

#### Issue 6: Linux - "webkit2gtk not found"

**Error:**
```
Package webkit2gtk-4.1 was not found
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install libwebkit2gtk-4.1-dev

# On older versions, try:
sudo apt install libwebkit2gtk-4.0-dev
```

#### Issue 7: Windows - "MSVC not found"

**Error:**
```
error: linker `link.exe` not found
```

**Solution:**
- Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Select "Desktop development with C++" during installation
- Restart terminal after installation

#### Issue 8: Build fails with "out of memory"

**Error:**
```
LLVM ERROR: out of memory
```

**Solution:**
```bash
# Build with fewer parallel jobs
cd src-tauri
cargo build -j 2

# Or close other applications to free RAM
```

#### Issue 9: Port 1420 already in use

**Error:**
```
Port 1420 is in use, trying another one...
Error: Port 1420 is in use
```

**Solution:**
```bash
# Find process using port 1420
lsof -ti:1420

# Kill the process (macOS/Linux)
kill $(lsof -ti:1420)

# Or use a different port by setting TAURI_DEV_HOST
# (Advanced - not recommended for beginners)
```

### Getting More Help

If you encounter issues not covered here:

1. **Check detailed documentation:**
   - [Troubleshooting Guide](troubleshooting.md)
   - [Setup Issues](setup-issues.md)
   - [Installation History](installation-history.md)

2. **Check logs:**
   ```bash
   # Run with verbose output
   RUST_LOG=debug bun run tauri dev
   ```

3. **Community Support:**
   - [GitHub Issues](https://github.com/getAsterisk/opcode/issues)
   - [Discord Server](https://discord.com/invite/KYwhHVzUsY)

4. **Verify your environment:**
   ```bash
   # Create a verification script
   cat > verify.sh << 'EOF'
   #!/bin/bash
   echo "=== opcode Environment Verification ==="
   echo "Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
   echo "Bun: $(bun --version 2>/dev/null || echo 'Not installed')"
   echo "Rust: $(rustc --version 2>/dev/null || echo 'Not installed')"
   echo "Cargo: $(cargo --version 2>/dev/null || echo 'Not installed')"
   echo "Claude: $(claude --version 2>/dev/null || echo 'Not installed')"
   echo "Git: $(git --version 2>/dev/null || echo 'Not installed')"
   echo "Platform: $(uname -s)"
   echo "Architecture: $(uname -m)"
   EOF

   chmod +x verify.sh
   ./verify.sh
   ```

---

## Next Steps

Once opcode is running successfully:

### 1. Explore the Interface
- **Projects View:** Browse your Claude Code projects in `~/.claude/projects/`
- **CC Agents:** Create custom AI agents with specialized prompts
- **Settings:** Configure application preferences

### 2. Create Your First Agent
```
Navigate to: CC Agents → Create Agent → Configure settings → Execute
```

### 3. View Usage Analytics
```
Menu → Usage Dashboard → View API costs and token usage
```

### 4. Try Timeline Features
- Create checkpoints during coding sessions
- Navigate session history
- Compare changes between checkpoints

### 5. Learn Development Workflow
- Read [Development Workflow](development-workflow.md) for contribution guidelines
- Check [Architecture](architecture.md) to understand the codebase
- Review [Commands Reference](commands-reference.md) for all available commands

### 6. Build for Production (Optional)

When ready to create a production build:

```bash
# Build optimized executable
bun run tauri build

# Find your installer in:
# - macOS: src-tauri/target/release/bundle/dmg/
# - Linux: src-tauri/target/release/bundle/deb/ (or appimage/, rpm/)
# - Windows: src-tauri/target/release/bundle/msi/
```

**Production build time:** ~2-5 minutes (includes optimizations)

---

## Quick Reference

### Essential Commands

```bash
# Install dependencies
bun install

# Build frontend (required before running)
bun run build

# Run desktop app
bun run tauri dev

# Build production version
bun run tauri build

# Using Just
just dev      # Build and run
just quick    # Same as above
just web      # Web server mode
just test     # Run Rust tests
just fmt      # Format code
just clean    # Clean build artifacts

# Verify installation
claude --version
bun --version
cargo --version
```

### Important Paths

- **Bun:** `~/.bun/bin/bun`
- **Cargo:** `~/.cargo/bin/cargo`
- **Claude Data:** `~/.claude/projects/`
- **Build Output:** `src-tauri/target/release/`
- **Frontend Dist:** `dist/`

### Port Configuration

- **Frontend Dev Server:** 1420 (Vite)
- **HMR (Hot Module Reload):** 1421
- **Web Server Mode:** 8080 (default, configurable)

### Key Configuration Files

- **Frontend:** `vite.config.ts`
- **Tauri:** `src-tauri/tauri.conf.json`
- **Rust:** `src-tauri/Cargo.toml`
- **Dependencies:** `package.json`
- **Build Automation:** `justfile`

---

## Checklist

Use this checklist to ensure everything is set up correctly:

- [ ] Claude Code CLI installed and accessible (`claude --version` works)
- [ ] Bun installed (`bun --version` shows 1.0.0+)
- [ ] Rust installed (`rustc --version` shows 1.70.0+)
- [ ] Cargo in PATH (`cargo --version` works)
- [ ] Platform-specific dependencies installed (see Platform-Specific Dependencies section)
- [ ] Repository cloned (`cd opcode` succeeds)
- [ ] Frontend dependencies installed (`bun install` completed)
- [ ] Frontend built (`dist/` folder exists)
- [ ] Application runs without errors (`bun run tauri dev` succeeds)
- [ ] Application window opens and is functional
- [ ] `~/.claude` directory exists (or will be created by Claude Code)

---

**Congratulations!** You now have opcode running on your machine. Happy coding with Claude!

For more information, see:
- [README.md](../README.md) - Full project overview
- [Architecture](architecture.md) - Technical architecture details
- [Development Workflow](development-workflow.md) - Contributing guidelines
- [CLAUDE.md](../CLAUDE.md) - Comprehensive development notes
