# Opcode - Development Notes

## Quick Start

### Prerequisites
- **Bun**: JavaScript runtime and package manager
- **Rust**: For Tauri backend compilation
- **Claude Code CLI**: Must be installed and available in PATH

### Running the App

```bash
# First time setup or after frontend changes:
bun install
bun run build

# Start the desktop app (make sure cargo env is loaded):
source "$HOME/.cargo/env" && bun run tauri dev

# Or if you've added cargo to your shell profile, just:
bun run tauri dev
```

### Using Just (Alternative)
```bash
just dev      # Build frontend and run desktop app
just quick    # Same as above
just web      # Run web server version (for mobile access)
```

## Project Architecture

### Key Understanding

This project has an **unusual Tauri workflow**:
1. **Frontend must be built FIRST** before running Tauri
2. The `beforeDevCommand` in tauri.conf.json is intentionally empty
3. This is NOT a hot-reload dev setup - you build once, then run

### Multiple Binaries

The project defines two binaries in `src-tauri/Cargo.toml`:
- `opcode` (main desktop app) - runs the Tauri GUI
- `opcode-web` (web server) - runs a web server for mobile/browser access

**Solution**: Added `default-run = "opcode"` to tell Cargo which binary to use by default.

## Setup Issues & Fixes

### Issue 1: Multiple Binaries Error
**Error**:
```
cargo run could not determine which binary to run
available binaries: opcode, opcode-web
```

**Fix**: Added to `[package]` section in `src-tauri/Cargo.toml:8`:
```toml
default-run = "opcode"
```

### Issue 2: Missing Frontend Build
**Error**:
```
The `frontendDist` configuration is set to `"../dist"` but this path doesn't exist
```

**Fix**: Must run `bun run build` before `tauri dev` to generate the `dist/` folder.

### Issue 3: Cargo Environment Not Loaded
**Error**:
```
failed to get cargo metadata: No such file or directory (os error 2)
```

**Fix**: The Cargo environment needs to be sourced before running Tauri. Use:
```bash
source "$HOME/.cargo/env" && bun run tauri dev
```

**Better Solution**: Add to your shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
source "$HOME/.cargo/env"
```
Then restart your terminal or run `exec $SHELL`.

## Project Structure

```
opcode/
├── src/                    # React frontend (TypeScript)
│   ├── components/         # UI components
│   ├── lib/               # API adapters & utilities
│   └── assets/            # Static assets
├── src-tauri/             # Rust backend (Tauri)
│   ├── src/
│   │   ├── main.rs        # Desktop app binary
│   │   ├── web_main.rs    # Web server binary
│   │   ├── commands/      # Tauri command handlers
│   │   ├── checkpoint/    # Timeline/checkpoint system
│   │   ├── process/       # Claude process management
│   │   └── web_server.rs  # Web server implementation
│   └── Cargo.toml         # Rust dependencies & config
├── dist/                  # Built frontend (generated)
├── justfile              # Just commands (alternative build tool)
├── vite.config.ts        # Vite configuration
└── package.json          # Frontend dependencies
```

## Development Workflow

### Standard Development
1. Make frontend changes in `src/`
2. Run `bun run build` to rebuild
3. App auto-reloads if `tauri dev` is running

### Rust Changes
The Tauri dev server watches Rust files and recompiles automatically.

### Web Server Mode
For testing on mobile devices:
```bash
just web            # Runs on port 8080
just web-port 3000  # Custom port
just ip             # Show your local IP
```

## Important Files

- **src-tauri/Cargo.toml** - Rust configuration, defines binaries
- **src-tauri/tauri.conf.json** - Tauri app configuration
- **vite.config.ts** - Frontend dev server (port 1420)
- **justfile** - Build commands reference
- **web_server.design.md** - Web server architecture details

## Common Commands

```bash
# Development
bun install                  # Install dependencies
bun run build               # Build frontend
bun run tauri dev           # Run desktop app
bun run tauri build         # Production build

# Alternative with Just
just dev                    # Quick start
just build-frontend         # Build only frontend
just clean                  # Clean all artifacts
just test                   # Run Rust tests
just fmt                    # Format Rust code

# Manual cargo commands
cd src-tauri
cargo run --bin opcode      # Run desktop app
cargo run --bin opcode-web  # Run web server
cargo build --release       # Release build
```

## Notes

- The project uses **Bun** instead of npm/yarn
- Frontend runs on port **1420** in dev mode
- Web server runs on port **8080** by default
- The app requires `~/.claude` directory for Claude Code data
- Built executables are in `src-tauri/target/release/`

## Troubleshooting

### "cargo not found"
```bash
source "$HOME/.cargo/env"
```

### "bun not found"
```bash
exec /bin/zsh  # or restart terminal
```

### "dist/ doesn't exist"
```bash
bun run build
```

### Multiple binary error
Ensure `default-run = "opcode"` is in Cargo.toml [package] section.

## Critical Research Findings

### What I Almost Did WRONG ❌

I initially tried to fix the multiple binaries issue by editing `tauri.conf.json` to add:
```json
"build": {
  "runner": "cargo",
  "targets": {
    "dev": {
      "args": ["--bin", "opcode"]
    }
  }
}
```

**This is WRONG!** Tauri 2 does NOT support this configuration structure. The `runner` field only accepts a string (the binary name), not an object with arguments.

### The RIGHT Solution ✅

After web research, I found that the correct Rust/Cargo way is to add `default-run = "opcode"` to the `[package]` section in `Cargo.toml`. This is the standard approach for Cargo projects with multiple binaries.

**Sources**:
- Stack Overflow discussion on Tauri with multiple binaries
- GitHub tauri-apps/tauri discussions #7592
- Tauri 2 configuration schema documentation

### Manual Testing First

We tested the fix manually before making it permanent:
```bash
bun run tauri dev -- --bin opcode
```

This confirmed the approach worked before editing Cargo.toml. **Always test manually first!**

## Installation History

### System Environment
- **OS**: macOS (Darwin 24.4.0)
- **Architecture**: Apple Silicon (aarch64-apple-darwin)
- **Date**: October 2025

### Installation Steps Executed

1. **Installed Bun**:
```bash
curl -fsSL https://bun.sh/install | bash
# Installed to: ~/.bun/bin/bun
# Version: 1.3.0
```

2. **Installed Rust**:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
# Installed: rustc 1.90.0
# Toolchain: stable-aarch64-apple-darwin
```

3. **Installed Dependencies**:
```bash
bun install
# Installed 409 packages in 9.07s
```

4. **Built Frontend**:
```bash
bun run build
# Generated dist/ folder with React app
# Build time: ~3.7s
```

5. **First Rust Compilation**:
```bash
bun run tauri dev
# First compile: ~19 seconds
# Downloaded 600+ crates
# Generated 651 build artifacts
```

## Compilation Notes

### Build Times
- **First compile**: ~19 seconds (downloads all crates)
- **Subsequent compiles**: ~1-2 seconds (cached)
- **Frontend build**: ~3-4 seconds

### Warnings (Non-Critical)
The codebase has some Rust warnings:
- `non_snake_case` warnings in `web_server.rs:236` and `:244`
- `dead_code` warning for unused `register_sidecar_process` method
These don't affect functionality but could be cleaned up.

## Web Server Mode - Critical Issues ⚠️

The `opcode-web` binary provides browser/mobile access, but `web_server.design.md` documents **CRITICAL BUGS**:

### Known Issues (from web_server.design.md):

1. **Session-scoped event dispatching BROKEN** 🔴
   - Sessions interfere with each other
   - Events are global, not session-specific
   - Multiple users will see each other's output

2. **Process cancellation NOT IMPLEMENTED** 🔴
   - Cancel button does nothing
   - No way to stop running Claude processes
   - Processes continue running in background

3. **stderr not captured** 🟡
   - Error messages from Claude not shown
   - Only stdout is displayed

4. **Missing claude-cancelled events** 🟡
   - Desktop app emits these, web server doesn't
   - Inconsistent behavior between modes

**Status**: Web server mode works for **single user, single session only**. Not production-ready.

## Advanced Usage

### Running Both Binaries

```bash
# Desktop app (Tauri GUI)
cargo run --bin opcode

# Web server (browser access)
cargo run --bin opcode-web -- --port 8080
```

### Manual CLI Command Passing

To pass arguments through Tauri CLI to Cargo:
```bash
tauri dev -- [cargo-args] -- [app-args]
```

Example:
```bash
tauri dev -- --bin opcode -- --some-app-flag
```

### Production Build

```bash
bun run tauri build
# Creates installers:
# - macOS: .dmg and .app in src-tauri/target/release/
# - Linux: .deb, .AppImage, .rpm
# - Windows: .msi, .exe
```

## Important Paths

- **Bun**: `~/.bun/bin/bun`
- **Cargo**: `~/.cargo/bin/cargo`
- **Claude Data**: `~/.claude/projects/`
- **Build Output**: `src-tauri/target/release/`
- **Frontend Dist**: `dist/`

## Configuration Files Deep Dive

### tauri.conf.json
```json
{
  "build": {
    "beforeDevCommand": "",  // Intentionally empty!
    "beforeBuildCommand": "bun run build",
    "frontendDist": "../dist"
  }
}
```
**Note**: `beforeDevCommand` is empty because we manually build first.

### vite.config.ts
- Dev server port: **1420** (Tauri expects this)
- HMR port: **1421**
- Watches: Ignores `src-tauri/**`

### Cargo.toml
```toml
[package]
default-run = "opcode"  # CRITICAL: Added to fix multiple binaries

[[bin]]
name = "opcode"         # Desktop GUI
path = "src/main.rs"

[[bin]]
name = "opcode-web"     # Web server
path = "src/web_main.rs"
```

## Lessons Learned

1. **Always research before editing** - Web search revealed the right solution
2. **Test manually first** - Confirmed the approach before permanent changes
3. **Read the justfile** - It documents the intended workflow
4. **This is NOT typical Tauri** - Build-first workflow is unusual
5. **Two binaries = two modes** - Desktop GUI vs web server for mobile

## References

- [Tauri Documentation](https://tauri.app/)
- [Bun Documentation](https://bun.sh/)
- [Cargo default-run documentation](https://doc.rust-lang.org/cargo/reference/manifest.html)
- See `web_server.design.md` for web server architecture details (including critical bugs)
- See `README.md` for full project documentation
- See `justfile` for intended build workflow
