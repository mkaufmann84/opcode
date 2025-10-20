# Opcode Commands Reference

Complete command reference for Opcode development, build, and deployment workflows.

---

## Table of Contents

- [Quick Reference](#quick-reference)
- [Package Manager Commands (Bun)](#package-manager-commands-bun)
- [Just Commands](#just-commands)
- [Cargo Commands](#cargo-commands)
- [Tauri CLI Commands](#tauri-cli-commands)
- [NPM Scripts](#npm-scripts)
- [Utility Scripts](#utility-scripts)
- [Command Workflows](#command-workflows)
- [Troubleshooting Commands](#troubleshooting-commands)

---

## Quick Reference

### Most Common Commands

```bash
# First-time setup
bun install                           # Install all dependencies
bun run build                         # Build frontend
bun run tauri dev                     # Start desktop app

# Development workflow (alternative)
just dev                              # Build frontend + run app
just quick                            # Same as above (alias)

# Testing and quality
just test                             # Run Rust tests
just fmt                              # Format Rust code
bun run check                         # Type-check TypeScript + Cargo check

# Production build
bun run tauri build                   # Build production app with installers

# Web server mode (for mobile access)
just web                              # Run web server on port 8080
just web-port 3000                    # Run on custom port
just ip                               # Show your local IP address
```

---

## Package Manager Commands (Bun)

Bun is the primary package manager for this project. It's faster than npm/yarn and serves as the JavaScript runtime.

### Installation Commands

#### `bun install`
**What it does**: Installs all dependencies from package.json
**When to use**: First-time setup or after pulling changes
**Performance**: ~5-10 seconds for full install (409 packages)
**Prerequisites**: None

```bash
bun install

# Alias
bun i
```

**Output Example**:
```
[409/409] packages installed [9.07s]
```

**Troubleshooting**:
- If it fails, delete `node_modules` and `bun.lockb`, then retry
- Ensure you have enough disk space (~500MB for node_modules)

---

#### `bun add <package>`
**What it does**: Adds a new dependency to package.json
**When to use**: Installing new packages
**Flags**:
- `-d` or `--dev`: Add as devDependency
- `-g` or `--global`: Install globally
- `--exact`: Pin to exact version

```bash
bun add react-icons              # Production dependency
bun add -d @types/node           # Dev dependency
bun add react@18.3.1 --exact     # Exact version
```

**Related**: `bun remove`, `bun update`

---

#### `bun remove <package>`
**What it does**: Removes a dependency from package.json
**When to use**: Uninstalling packages

```bash
bun remove lodash
bun rm lodash                    # Alias
```

---

#### `bun update <package>`
**What it does**: Updates package(s) to latest version
**When to use**: Updating dependencies

```bash
bun update                       # Update all packages
bun update react react-dom       # Update specific packages
```

**Related**: `bun outdated` (shows outdated packages)

---

### Build and Run Commands

#### `bun run <script>`
**What it does**: Runs a script from package.json
**When to use**: Executing npm scripts

```bash
bun run build                    # Build frontend
bun run dev                      # Start Vite dev server
bun run tauri dev                # Start Tauri dev mode
```

**Performance**: Faster than `npm run` by ~2x

---

#### `bun run build`
**What it does**: Compiles TypeScript and builds frontend with Vite
**When to use**: Before running Tauri, or for production builds
**Performance**: ~3-4 seconds
**Output**: Generates `dist/` folder
**Prerequisites**: None

```bash
bun run build
```

**Output Example**:
```
vite v6.0.3 building for production...
✓ 127 modules transformed.
dist/index.html                   0.52 kB │ gzip:  0.31 kB
dist/assets/index-CrF3xK9s.css   89.21 kB │ gzip: 13.45 kB
dist/assets/index-BkL4xYz2.js   432.14 kB │ gzip: 125.33 kB
✓ built in 3.72s
```

**Troubleshooting**:
- If TypeScript errors occur, run `bun run check` first
- Clear cache with `rm -rf dist node_modules/.vite`

**Related**: `bun run preview` (preview production build)

---

#### `bun run dev`
**What it does**: Starts Vite dev server with hot module replacement
**When to use**: Frontend-only development
**Port**: 1420 (configured in vite.config.ts)
**URL**: http://localhost:1420
**Prerequisites**: None

```bash
bun run dev
```

**Note**: This does NOT start Tauri. Use `bun run tauri dev` for full app.

**Output Example**:
```
VITE v6.0.3  ready in 842 ms

  ➜  Local:   http://localhost:1420/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Flags**:
- `--host`: Expose to network
- `--port <number>`: Change port

---

#### `bun run preview`
**What it does**: Serves production build locally for testing
**When to use**: Testing production build before deploying
**Prerequisites**: Must run `bun run build` first

```bash
bun run build
bun run preview
```

---

### Testing and Quality Commands

#### `bun run check`
**What it does**: Type-checks TypeScript and runs cargo check
**When to use**: Before committing, to catch type errors
**Performance**: ~5-10 seconds
**Prerequisites**: None

```bash
bun run check
```

**Equivalent to**:
```bash
tsc --noEmit && cd src-tauri && cargo check
```

**Output**: No output if successful, errors if type issues found

---

#### `bun test`
**What it does**: Runs Bun's built-in test runner
**When to use**: Running JavaScript/TypeScript tests
**Prerequisites**: Test files must exist

```bash
bun test
```

**Note**: This project uses Cargo tests for Rust. Frontend tests not currently configured.

---

### Advanced Bun Commands

#### `bun x <command>` (bunx)
**What it does**: Executes a package binary without installing
**When to use**: Running CLI tools temporarily

```bash
bun x eslint src/           # Run ESLint without installing
```

**Equivalent**: `npx` in npm

---

#### `bun audit`
**What it does**: Checks for security vulnerabilities
**When to use**: Regular security audits

```bash
bun audit
```

---

#### `bun outdated`
**What it does**: Shows outdated dependencies
**When to use**: Checking for updates

```bash
bun outdated
```

---

#### `bun info <package>`
**What it does**: Shows package metadata from registry
**When to use**: Researching packages

```bash
bun info react
```

---

#### `bun why <package>`
**What it does**: Explains why a package is installed
**When to use**: Debugging dependency trees

```bash
bun why react-dom
```

---

## Just Commands

Just is a command runner (like Make) that simplifies common workflows. The `justfile` contains predefined commands.

### Core Development Commands

#### `just` or `just --list`
**What it does**: Shows all available Just commands
**When to use**: Discovering available commands

```bash
just
just --list
```

**Output**:
```
Available recipes:
    default
    shell
    install
    build-frontend
    build-backend
    ...
```

---

#### `just dev`
**What it does**: Builds frontend, then runs desktop app
**When to use**: Standard development workflow
**Performance**: ~3-4s build + ~1-2s cargo run
**Prerequisites**: Cargo environment loaded

```bash
just dev
```

**Equivalent to**:
```bash
npm run build && cd src-tauri && cargo run
```

**Note**: NOT hot-reload - rebuild frontend to see changes

---

#### `just quick`
**What it does**: Alias for `just dev`
**When to use**: Quick development cycle

```bash
just quick
```

---

#### `just run`
**What it does**: Builds frontend and runs app in debug mode
**When to use**: Same as `just dev`

```bash
just run
```

---

#### `just run-release`
**What it does**: Builds frontend + backend in release mode, then runs
**When to use**: Testing production performance
**Performance**: First build ~19s, subsequent ~1-2s

```bash
just run-release
```

**Output location**: `src-tauri/target/release/opcode`

---

### Build Commands

#### `just install`
**What it does**: Installs frontend dependencies (npm install)
**When to use**: First-time setup

```bash
just install
```

**Note**: Uses npm by default. Consider changing to `bun install` in justfile.

---

#### `just build-frontend`
**What it does**: Builds React frontend only
**When to use**: Preparing for Tauri build
**Output**: `dist/` folder

```bash
just build-frontend
```

**Equivalent**: `npm run build`

---

#### `just build-backend`
**What it does**: Compiles Rust backend in debug mode
**When to use**: Backend-only development
**Performance**: ~1-2s (cached), ~19s (clean build)

```bash
just build-backend
```

**Equivalent**:
```bash
cd src-tauri && cargo build
```

---

#### `just build-backend-release`
**What it does**: Compiles Rust backend in release mode
**When to use**: Production builds, performance testing
**Performance**: ~19s (clean), ~2-3s (cached)
**Optimizations**: Full LTO, size optimization, stripped symbols

```bash
just build-backend-release
```

**Equivalent**:
```bash
cd src-tauri && cargo build --release
```

**Profile settings** (from Cargo.toml):
```toml
[profile.release]
strip = true           # Remove debug symbols
opt-level = "z"        # Optimize for size
lto = true             # Link-time optimization
codegen-units = 1      # Single codegen unit (slower build, faster runtime)
```

---

#### `just build`
**What it does**: Full build - installs deps, builds frontend, builds backend
**When to use**: First-time setup or clean build
**Performance**: ~30-40s (clean), ~5-10s (cached)

```bash
just build
```

**Equivalent**:
```bash
npm install && npm run build && cd src-tauri && cargo build
```

---

#### `just rebuild`
**What it does**: Cleans everything, then rebuilds from scratch
**When to use**: Fixing build issues, starting fresh
**Performance**: ~45-60s

```bash
just rebuild
```

**Equivalent**:
```bash
rm -rf node_modules dist && cd src-tauri && cargo clean && npm install && npm run build && cargo run
```

**Warning**: Deletes all build artifacts and dependencies

---

### Testing and Quality Commands

#### `just test`
**What it does**: Runs Rust test suite
**When to use**: Before committing, CI/CD
**Prerequisites**: None

```bash
just test
```

**Equivalent**:
```bash
cd src-tauri && cargo test
```

**Options**:
```bash
cd src-tauri && cargo test --release    # Test in release mode
cd src-tauri && cargo test -- --nocapture  # Show println! output
cd src-tauri && cargo test test_name    # Run specific test
```

---

#### `just fmt`
**What it does**: Formats Rust code with rustfmt
**When to use**: Before committing
**Prerequisites**: None

```bash
just fmt
```

**Equivalent**:
```bash
cd src-tauri && cargo fmt
```

**Check without modifying**:
```bash
cd src-tauri && cargo fmt --check
```

---

#### `just check`
**What it does**: Checks Rust code for errors (no build)
**When to use**: Quick error checking
**Performance**: Faster than full build

```bash
just check
```

**Equivalent**:
```bash
cd src-tauri && cargo check
```

---

### Web Server Commands

#### `just web`
**What it does**: Runs web server for browser/mobile access
**When to use**: Testing on phones or tablets
**Port**: 8080 (default)
**URL**: http://YOUR_IP:8080

```bash
just web
```

**Equivalent**:
```bash
npm run build && cd src-tauri && cargo run --bin opcode-web
```

**Important**: See CLAUDE.md for critical web server bugs:
- Session-scoped events broken (multi-user issues)
- Cancel button not implemented
- stderr not captured

---

#### `just web-port <PORT>`
**What it does**: Runs web server on custom port
**When to use**: Port 8080 is occupied

```bash
just web-port 3000
just web-port 5000
```

**Equivalent**:
```bash
cargo run --bin opcode-web -- --port 3000
```

---

#### `just ip`
**What it does**: Shows your local IP address for phone access
**When to use**: Connecting from mobile device

```bash
just ip
```

**Output Example**:
```
🌐 Your PC's IP addresses:
192.168.1.100

📱 Use this IP on your phone: http://192.168.1.100:8080
```

---

### Utility Commands

#### `just clean`
**What it does**: Removes all build artifacts
**When to use**: Freeing disk space, fixing build issues
**Disk space freed**: ~2-5GB

```bash
just clean
```

**Equivalent**:
```bash
rm -rf node_modules dist
cd src-tauri && cargo clean
```

**Warning**: Requires re-download of all dependencies

---

#### `just shell`
**What it does**: Enters Nix development environment
**When to use**: NixOS users only

```bash
just shell
```

**Note**: Not applicable for macOS/Windows

---

#### `just info`
**What it does**: Shows project information and common commands
**When to use**: Quick reference

```bash
just info
```

**Output**:
```
🚀 Opcode - Claude Code GUI Application
Built for NixOS without Docker

📦 Frontend: React + TypeScript + Vite
🦀 Backend: Rust + Tauri
🏗️  Build System: Nix + Just

💡 Common commands:
  just run      - Build and run (desktop)
  just web      - Run web server for phone access
  just quick    - Quick build and run
  just rebuild  - Full clean rebuild
  just shell    - Enter Nix environment
  just ip       - Show IP for phone access
```

---

## Cargo Commands

Cargo is Rust's package manager and build system. All commands run from `src-tauri/` directory.

### Build Commands

#### `cargo build`
**What it does**: Compiles Rust code in debug mode
**When to use**: Development builds
**Performance**: ~1-2s (incremental), ~19s (clean)
**Output**: `target/debug/opcode` and `target/debug/opcode-web`

```bash
cd src-tauri
cargo build
```

**Options**:
- `--release`: Release mode (optimized)
- `--bin opcode`: Build only desktop app
- `--bin opcode-web`: Build only web server
- `--all-targets`: Build all targets (bins, libs, tests)
- `--lib`: Build only library
- `--workspace`: Build all workspace packages

**Examples**:
```bash
cargo build --release                    # Production build
cargo build --bin opcode                 # Desktop only
cargo build --bin opcode-web             # Web server only
cargo build --release --bin opcode       # Release desktop app
cargo build --target x86_64-apple-darwin # Specific target
```

**Flags**:
- `-v, --verbose`: Show detailed output
- `-q, --quiet`: Suppress cargo output
- `-j, --jobs N`: Parallel jobs (default: # CPUs)
- `--locked`: Ensure Cargo.lock unchanged
- `--offline`: Build without network access
- `--timings`: Generate build timing report

**Profile-specific builds**:
```bash
cargo build --profile <profile-name>
```

---

#### `cargo build --release`
**What it does**: Compiles with full optimizations
**When to use**: Production, performance testing, final builds
**Performance**: ~19s (clean), ~2-3s (incremental)
**Output**: `target/release/opcode` (stripped, optimized)
**Size**: ~50% smaller than debug build

```bash
cd src-tauri
cargo build --release
```

**Optimizations applied** (from Cargo.toml):
```
- Strip debug symbols (strip = true)
- Size optimization (opt-level = "z")
- Link-time optimization (lto = true)
- Single codegen unit (codegen-units = 1)
```

**Use cases**:
- Final distribution builds
- Performance benchmarking
- Production deployments
- App store submissions

---

#### `cargo clean`
**What it does**: Removes all build artifacts
**When to use**: Fixing build issues, freeing space
**Disk space freed**: ~2-4GB

```bash
cd src-tauri
cargo clean
```

**Options**:
- `--release`: Clean only release artifacts
- `--doc`: Clean only documentation
- `--target <triple>`: Clean specific target

**Warning**: Next build will be full rebuild (~19s)

---

### Run Commands

#### `cargo run`
**What it does**: Builds and runs the default binary (opcode)
**When to use**: Quick development testing
**Prerequisites**: Frontend must be built (`bun run build`)

```bash
cd src-tauri
cargo run
```

**Equivalent**: `cargo build && ./target/debug/opcode`

**Options**:
- `--release`: Run in release mode
- `--bin <name>`: Run specific binary
- `-- <args>`: Pass arguments to app

**Examples**:
```bash
cargo run                              # Run opcode (debug)
cargo run --release                    # Run opcode (release)
cargo run --bin opcode-web             # Run web server
cargo run --bin opcode-web -- --port 8080  # Web server with args
```

**Common error**:
```
The `frontendDist` configuration is set to `"../dist"` but this path doesn't exist
```
**Solution**: Run `bun run build` first

---

#### `cargo run --bin opcode`
**What it does**: Runs desktop app explicitly
**When to use**: When multiple binaries exist

```bash
cd src-tauri
cargo run --bin opcode
```

**Note**: `default-run = "opcode"` in Cargo.toml makes this the default

---

#### `cargo run --bin opcode-web`
**What it does**: Runs web server for browser access
**When to use**: Mobile/browser testing
**Port**: 8080 (default)

```bash
cd src-tauri
cargo run --bin opcode-web

# With custom port
cargo run --bin opcode-web -- --port 3000
```

**Access**: http://localhost:8080

---

### Testing Commands

#### `cargo test`
**What it does**: Runs all tests (unit + integration)
**When to use**: Before committing, CI/CD
**Performance**: Varies based on test count

```bash
cd src-tauri
cargo test
```

**Options**:
- `--release`: Test in release mode
- `--lib`: Test only library
- `--bins`: Test all binaries
- `--test <name>`: Run specific test file
- `--no-run`: Compile tests but don't run
- `--no-fail-fast`: Run all tests even if some fail
- `-q, --quiet`: Less verbose output

**Examples**:
```bash
cargo test                              # All tests
cargo test test_checkpoint              # Tests matching name
cargo test --release                    # Release mode tests
cargo test -- --nocapture               # Show println! output
cargo test -- --test-threads=1          # Single-threaded
cargo test --lib                        # Library tests only
cargo test --bin opcode                 # Binary tests only
```

**Filtering**:
```bash
cargo test checkpoint      # Tests with "checkpoint" in name
cargo test db::            # Tests in db module
```

**Test binary arguments** (after `--`):
- `--nocapture`: Show stdout/stderr
- `--test-threads=N`: Parallel test threads
- `--ignored`: Run ignored tests
- `--include-ignored`: Run all tests including ignored
- `--show-output`: Show successful test output

---

#### `cargo bench`
**What it does**: Runs benchmark tests
**When to use**: Performance testing

```bash
cd src-tauri
cargo bench
```

**Note**: Requires benchmark targets in Cargo.toml

---

### Code Quality Commands

#### `cargo check`
**What it does**: Checks code for errors without building
**When to use**: Quick error checking
**Performance**: Much faster than `cargo build`

```bash
cd src-tauri
cargo check
```

**Options**:
- `--all-targets`: Check all targets
- `--lib`: Check only library
- `--bins`: Check all binaries

**Use case**: Fast feedback during development

---

#### `cargo clippy`
**What it does**: Lints code for common mistakes
**When to use**: Before committing, code reviews
**Prerequisites**: `rustup component add clippy`

```bash
cd src-tauri
cargo clippy
```

**Options**:
- `--fix`: Auto-fix issues
- `--no-deps`: Don't lint dependencies
- `-- -W clippy::pedantic`: Enable pedantic lints
- `-- -D warnings`: Treat warnings as errors

**Examples**:
```bash
cargo clippy                            # Basic linting
cargo clippy --fix                      # Auto-fix
cargo clippy -- -W clippy::all          # All lints
cargo clippy -- -D warnings             # Deny warnings
cargo clippy --no-deps                  # Skip dependencies
```

**Common lint flags**:
```bash
-W clippy::pedantic      # Pedantic lints
-W clippy::nursery       # Experimental lints
-W clippy::cargo         # Cargo.toml lints
-A clippy::too_many_arguments  # Allow specific lint
```

**Project-specific**:
- Known warnings in `web_server.rs` (non-critical)
- `dead_code` warning for `register_sidecar_process`

---

#### `cargo fmt`
**What it does**: Formats code according to Rust style guide
**When to use**: Before every commit

```bash
cd src-tauri
cargo fmt
```

**Check without modifying**:
```bash
cargo fmt --check
```

**Options**:
- `--all`: Format workspace
- `--check`: Check formatting without changes

**Integration**: Often added to pre-commit hooks

---

### Documentation Commands

#### `cargo doc`
**What it does**: Generates HTML documentation
**When to use**: Documenting APIs, onboarding
**Output**: `target/doc/opcode_lib/index.html`

```bash
cd src-tauri
cargo doc --open
```

**Options**:
- `--open`: Open in browser
- `--no-deps`: Skip dependencies
- `--document-private-items`: Include private items

---

### Dependency Commands

#### `cargo add <crate>`
**What it does**: Adds a dependency to Cargo.toml
**When to use**: Installing new crates

```bash
cd src-tauri
cargo add serde
cargo add tokio --features full
cargo add anyhow --dev
```

**Flags**:
- `--features <features>`: Enable features
- `--dev`: Add as dev-dependency
- `--build`: Add as build-dependency
- `--optional`: Make optional

---

#### `cargo remove <crate>`
**What it does**: Removes a dependency
**When to use**: Cleaning up unused crates

```bash
cd src-tauri
cargo remove uuid
```

---

#### `cargo update`
**What it does**: Updates dependencies in Cargo.lock
**When to use**: Updating to latest compatible versions

```bash
cd src-tauri
cargo update
cargo update -p serde    # Update specific package
```

---

#### `cargo tree`
**What it does**: Shows dependency tree
**When to use**: Understanding dependencies, debugging bloat

```bash
cd src-tauri
cargo tree
cargo tree -i serde      # Show inverse dependencies
cargo tree -d            # Show duplicates
```

---

### Advanced Cargo Commands

#### `cargo metadata`
**What it does**: Outputs project metadata as JSON
**When to use**: Build scripts, tooling integration

```bash
cd src-tauri
cargo metadata --format-version 1
```

---

#### `cargo vendor`
**What it does**: Vendors all dependencies locally
**When to use**: Offline builds, auditing dependencies

```bash
cd src-tauri
cargo vendor
```

---

#### `cargo install`
**What it does**: Installs a binary crate globally
**When to use**: Installing CLI tools

```bash
cargo install cargo-watch    # File watcher
cargo install cargo-edit     # cargo add/remove commands
cargo install cargo-audit    # Security auditing
```

**Installed binaries location**: `~/.cargo/bin/`

---

#### `cargo watch`
**What it does**: Runs command on file changes
**When to use**: Auto-recompilation during development
**Prerequisites**: `cargo install cargo-watch`

```bash
cd src-tauri
cargo watch -x run           # Auto-run on changes
cargo watch -x test          # Auto-test on changes
cargo watch -x check         # Auto-check on changes
```

---

#### `cargo audit`
**What it does**: Checks dependencies for security vulnerabilities
**When to use**: Security audits, CI/CD
**Prerequisites**: `cargo install cargo-audit`

```bash
cd src-tauri
cargo audit
```

---

#### `cargo expand`
**What it does**: Expands macros
**When to use**: Debugging macro issues
**Prerequisites**: `cargo install cargo-expand`

```bash
cd src-tauri
cargo expand
```

---

## Tauri CLI Commands

Tauri CLI manages the desktop application lifecycle. Invoked via `bun tauri` or `bun run tauri`.

### Development Commands

#### `tauri dev`
**What it does**: Runs app in development mode with auto-reload
**When to use**: Active development
**Prerequisites**: Frontend must be built first
**Port**: 1420 (Vite dev server)

```bash
bun run tauri dev
bun tauri dev          # Equivalent
```

**What happens**:
1. Reads `tauri.conf.json` for configuration
2. Runs `beforeDevCommand` (empty in this project)
3. Starts Rust file watcher
4. Compiles Rust code
5. Launches desktop window
6. Auto-reloads on Rust changes

**Options**:
- `--runner <RUNNER>`: Custom cargo runner
- `--target <TRIPLE>`: Build for specific target
- `--features <FEATURES>`: Cargo features to enable
- `--release`: Run in release mode
- `--no-watch`: Disable file watcher
- `--no-dev-server`: Disable dev server
- `--port <PORT>`: Dev server port (default: 1430)
- `--exit-on-panic`: Exit on Rust panic
- `-v, --verbose`: Verbose logging
- `-c, --config <CONFIG>`: Merge config files

**Examples**:
```bash
tauri dev                                  # Standard dev mode
tauri dev --release                        # Release mode with watcher
tauri dev --features logging               # Enable features
tauri dev --no-watch                       # No auto-reload
tauri dev -- --bin opcode                  # Pass cargo args
tauri dev -- -- --some-app-flag            # Pass app args
```

**Passing arguments**:
```bash
tauri dev -- [cargo-args] -- [app-args]
```

**Common issues**:
- "frontendDist doesn't exist": Run `bun run build` first
- "cargo not found": Source cargo env with `source ~/.cargo/env`
- Port 1420 in use: Change in vite.config.ts

**Performance**: First run ~19s, subsequent ~1-2s

---

#### `tauri build`
**What it does**: Creates production build with installers
**When to use**: Distribution, releases
**Performance**: ~30-60s
**Output**:
- macOS: `.dmg`, `.app` in `src-tauri/target/release/bundle/`
- Linux: `.deb`, `.AppImage`, `.rpm`
- Windows: `.msi`, `.exe`

```bash
bun run tauri build
```

**What happens**:
1. Runs `beforeBuildCommand` (`bun run build`)
2. Compiles Rust in release mode
3. Runs `beforeBundleCommand` (if configured)
4. Generates platform-specific bundles
5. Signs app (if configured)
6. Creates installers

**Options**:
- `-d, --debug`: Build in debug mode
- `-t, --target <TRIPLE>`: Target triple
- `-b, --bundles <BUNDLES>`: Specific bundles (app, dmg, ios)
- `--no-bundle`: Skip bundling step
- `--ci`: Skip prompts (for CI/CD)
- `-f, --features <FEATURES>`: Cargo features
- `-c, --config <CONFIG>`: Config overrides
- `-v, --verbose`: Verbose output

**Examples**:
```bash
tauri build                                # All bundles
tauri build --bundles dmg                  # DMG only
tauri build --target universal-apple-darwin  # Universal macOS
tauri build --debug                        # Debug build with bundles
tauri build --ci                           # CI mode (no prompts)
tauri build --features custom-protocol     # Production feature
```

**Platform-specific targets**:
```bash
# macOS
tauri build --target x86_64-apple-darwin       # Intel
tauri build --target aarch64-apple-darwin      # Apple Silicon
tauri build --target universal-apple-darwin    # Universal binary

# Linux
tauri build --target x86_64-unknown-linux-gnu

# Windows
tauri build --target x86_64-pc-windows-msvc
```

**Bundle outputs**:
```
src-tauri/target/release/bundle/
├── dmg/
│   └── Opcode_0.2.1_x64.dmg
├── macos/
│   └── Opcode.app
├── deb/
│   └── opcode_0.2.1_amd64.deb
└── appimage/
    └── opcode_0.2.1_amd64.AppImage
```

**Size**: ~15-30MB per bundle (depending on platform)

---

#### `bun run build:dmg`
**What it does**: Builds macOS DMG installer only
**When to use**: Quick macOS distribution

```bash
bun run build:dmg
```

**Equivalent**:
```bash
tauri build --bundles dmg
```

---

### Information Commands

#### `tauri info`
**What it does**: Shows environment information
**When to use**: Debugging, issue reporting

```bash
bun tauri info
```

**Output includes**:
- OS version
- Node.js version
- Rust version
- Cargo version
- Tauri CLI version
- Tauri dependencies versions
- Project configuration
- Active features
- Target triple

**Example output**:
```
[Environment]
  OS: macOS 14.4.0 X64
  Webview: macOS (WebKit 617.2.6)
  Node: 20.11.0
  npm: 10.2.4
  bun: 1.3.0
  rustc: 1.90.0
  cargo: 1.90.0
  rustup: 1.26.0

[Packages]
  @tauri-apps/cli: 2.7.1
  @tauri-apps/api: 2.1.1
  tauri: 2.0.0
  tauri-build: 2.0.0

[App]
  build-type: bundle
  CSP: default-src 'self'; script-src 'self'
  distDir: ../dist
  devPath: http://localhost:1420
```

**Options**:
- `--interactive`: Interactive mode with fixes
- `-v, --verbose`: More detailed output

---

### Utility Commands

#### `tauri icon`
**What it does**: Generates app icons for all platforms
**When to use**: Setting up app icons
**Input**: PNG or SVG file (1024x1024 recommended)
**Output**: Platform-specific icon files

```bash
bun tauri icon ./app-icon.png
```

**Default input**: `./app-icon.png`

**Options**:
- `-o, --output <DIR>`: Output directory (default: `icons/`)
- `-p, --png <SIZES>`: Custom PNG sizes
- `--ios-color <COLOR>`: iOS icon background color (default: #fff)

**Generated icons**:
- macOS: `.icns`
- Windows: `.ico`
- Linux: `.png` (various sizes)
- iOS: `.png` (App Store sizes)
- Android: `.png` (various densities)

**Example**:
```bash
tauri icon ./logo.png --output src-tauri/icons
```

---

#### `tauri init`
**What it does**: Initializes Tauri in existing project
**When to use**: Adding Tauri to existing web app

```bash
tauri init
```

**Note**: Not needed for this project (already initialized)

---

#### `tauri add <plugin>`
**What it does**: Adds Tauri plugin to project
**When to use**: Adding new capabilities

```bash
tauri add dialog
tauri add fs
tauri add shell
```

**What it does**:
1. Adds plugin to `Cargo.toml`
2. Adds plugin to `src-tauri/src/main.rs`
3. Updates permissions

---

#### `tauri remove <plugin>`
**What it does**: Removes Tauri plugin
**When to use**: Cleaning up unused plugins

```bash
tauri remove dialog
```

---

#### `tauri migrate`
**What it does**: Migrates from Tauri v1 to v2
**When to use**: Upgrading legacy projects

```bash
tauri migrate
```

**Note**: This project is already v2

---

#### `tauri completions <shell>`
**What it does**: Generates shell completions
**When to use**: Improving CLI experience
**Shells**: bash, zsh, fish, powershell

```bash
tauri completions bash > ~/.tauri-completions.bash
source ~/.tauri-completions.bash
```

---

### Advanced Commands

#### `tauri android`
**What it does**: Android-specific commands
**When to use**: Building for Android

```bash
tauri android init
tauri android dev
tauri android build
```

**Prerequisites**: Android SDK, NDK

---

#### `tauri ios`
**What it does**: iOS-specific commands
**When to use**: Building for iOS

```bash
tauri ios init
tauri ios dev
tauri ios build
```

**Prerequisites**: Xcode, iOS SDK

---

#### `tauri signer`
**What it does**: Manages code signing for updater
**When to use**: Setting up app updates

```bash
tauri signer generate
tauri signer sign <file>
```

---

#### `tauri inspect`
**What it does**: Inspects WebView for debugging
**When to use**: Debugging frontend issues

```bash
tauri inspect
```

---

## NPM Scripts

Scripts defined in `package.json`. Invoked via `bun run <script>`.

### Standard Scripts

#### `bun run dev`
**Script**: `vite`
**What it does**: Starts Vite dev server
**Port**: 1420

```bash
bun run dev
```

**Note**: Frontend-only, does NOT start Tauri

---

#### `bun run build`
**Script**: `tsc && vite build`
**What it does**: Type-checks then builds frontend
**Output**: `dist/` folder

```bash
bun run build
```

**Steps**:
1. `tsc`: Type-check TypeScript (no emit)
2. `vite build`: Build production bundle

---

#### `bun run preview`
**Script**: `vite preview`
**What it does**: Preview production build
**Prerequisites**: Must run `bun run build` first

```bash
bun run preview
```

---

#### `bun run tauri`
**Script**: `tauri`
**What it does**: Invokes Tauri CLI

```bash
bun run tauri dev
bun run tauri build
bun run tauri info
```

**Alias**: `bun tauri <command>`

---

#### `bun run check`
**Script**: `tsc --noEmit && cd src-tauri && cargo check`
**What it does**: Checks TypeScript and Rust for errors
**Performance**: ~5-10s

```bash
bun run check
```

**Use case**: Pre-commit checks, CI/CD

---

### Custom Build Scripts

#### `bun run build:dmg`
**Script**: `tauri build --bundles dmg`
**What it does**: Builds macOS DMG only

```bash
bun run build:dmg
```

---

#### `bun run build:executables`
**Script**: `bun run scripts/fetch-and-build.js --version=1.0.41`
**What it does**: Fetches and builds Claude executables
**When to use**: Setting up Claude Code binaries

```bash
bun run build:executables
```

**Note**: Requires `scripts/fetch-and-build.js` (check if exists)

---

#### `bun run build:executables:current`
**Script**: `bun run scripts/fetch-and-build.js current --version=1.0.41`
**What it does**: Builds for current platform only

```bash
bun run build:executables:current
```

---

#### `bun run build:executables:linux`
**Script**: `bun run scripts/fetch-and-build.js linux --version=1.0.41`
**What it does**: Builds Linux executables

```bash
bun run build:executables:linux
```

---

#### `bun run build:executables:macos`
**Script**: `bun run scripts/fetch-and-build.js macos --version=1.0.41`
**What it does**: Builds macOS executables

```bash
bun run build:executables:macos
```

---

#### `bun run build:executables:windows`
**Script**: `bun run scripts/fetch-and-build.js windows --version=1.0.41`
**What it does**: Builds Windows executables

```bash
bun run build:executables:windows
```

---

## Utility Scripts

### Version Bumping

#### `./scripts/bump-version.sh <version>`
**What it does**: Updates version across all config files
**When to use**: Preparing releases
**Files updated**:
- `package.json`
- `src-tauri/Cargo.toml`
- `src-tauri/tauri.conf.json`
- `src-tauri/Info.plist`

```bash
./scripts/bump-version.sh 0.3.0
```

**What it does**:
1. Updates version in all files
2. Shows git diff
3. Prints next steps (commit, tag, push)

**Example output**:
```
Bumping version to 0.3.0...
✅ Version bumped to 0.3.0 in all files

Next steps:
1. Review the changes: git diff
2. Commit: git commit -am "chore: bump version to v0.3.0"
3. Tag: git tag -a v0.3.0 -m "Release v0.3.0"
4. Push: git push && git push --tags
```

**Warning**: Creates `.bak` files temporarily (auto-deleted)

---

## Command Workflows

### First-Time Setup

```bash
# 1. Install Bun (if not installed)
curl -fsSL https://bun.sh/install | bash
exec $SHELL

# 2. Install Rust (if not installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# 3. Clone repository
git clone <repo-url>
cd opcode

# 4. Install dependencies
bun install

# 5. Build frontend
bun run build

# 6. Run app
bun run tauri dev

# Alternative: Use Just
just dev
```

---

### Daily Development Workflow

```bash
# Method 1: Manual
bun run build              # Rebuild frontend after changes
bun run tauri dev          # Start app

# Method 2: Just (recommended)
just dev                   # Build + run

# Method 3: Separate terminals
# Terminal 1: Frontend dev server (optional)
bun run dev

# Terminal 2: Tauri app
bun run tauri dev
```

**Note**: Frontend dev server NOT required for Tauri dev mode

---

### Testing Workflow

```bash
# 1. Check TypeScript types
bun run check

# 2. Format Rust code
just fmt

# 3. Lint Rust code
cd src-tauri && cargo clippy

# 4. Run tests
just test

# 5. Build release
cargo build --release
```

---

### Production Build Workflow

```bash
# 1. Bump version
./scripts/bump-version.sh 1.0.0

# 2. Review changes
git diff

# 3. Build frontend
bun run build

# 4. Build Tauri app
bun run tauri build

# 5. Test build
open src-tauri/target/release/bundle/dmg/Opcode_1.0.0_x64.dmg

# 6. Commit and tag
git commit -am "chore: bump version to v1.0.0"
git tag -a v1.0.0 -m "Release v1.0.0"
git push && git push --tags
```

---

### Web Server Workflow (Mobile Testing)

```bash
# 1. Build frontend
bun run build

# 2. Start web server
just web

# 3. Get your IP
just ip

# 4. On phone, open:
# http://YOUR_IP:8080

# Alternative: Custom port
just web-port 3000
```

**Important**: Web server has known bugs (see CLAUDE.md):
- Session-scoped events broken
- Cancel button not working
- Multi-user issues

---

### Clean Rebuild Workflow

```bash
# Option 1: Just
just rebuild

# Option 2: Manual
just clean
bun install
bun run build
cd src-tauri && cargo build

# Option 3: Nuclear (deletes everything)
rm -rf node_modules dist src-tauri/target bun.lockb
bun install
bun run build
cd src-tauri && cargo build
```

---

### Release Workflow (Full)

```bash
# 1. Clean build
just clean
bun install

# 2. Run all checks
bun run check
cd src-tauri && cargo clippy
just test

# 3. Bump version
./scripts/bump-version.sh 1.0.0

# 4. Build production
bun run build
bun run tauri build

# 5. Test installers
# macOS
open src-tauri/target/release/bundle/dmg/*.dmg

# Linux
sudo dpkg -i src-tauri/target/release/bundle/deb/*.deb

# 6. Git workflow
git add .
git commit -m "chore: release v1.0.0"
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin main --tags

# 7. Create GitHub release (optional)
gh release create v1.0.0 \
  src-tauri/target/release/bundle/dmg/*.dmg \
  src-tauri/target/release/bundle/deb/*.deb \
  --title "v1.0.0" \
  --notes "Release notes here"
```

---

### CI/CD Workflow

```bash
# Typical CI/CD pipeline commands

# 1. Install dependencies
bun install --frozen-lockfile

# 2. Lint and check
bun run check
cd src-tauri && cargo fmt --check
cd src-tauri && cargo clippy -- -D warnings

# 3. Test
cd src-tauri && cargo test --release

# 4. Build
bun run build
bun run tauri build --ci

# 5. Upload artifacts
# (varies by CI platform)
```

---

### Hot Reload Development (Rust + Frontend)

```bash
# Terminal 1: Watch Rust code
cd src-tauri
cargo watch -x run

# Terminal 2: Watch frontend (optional)
bun run dev

# Note: Tauri dev mode already watches Rust files
# cargo watch is optional for more control
```

---

## Troubleshooting Commands

### Diagnostic Commands

#### Check environment
```bash
bun --version
cargo --version
rustc --version
bun tauri info
```

---

#### Check disk space
```bash
du -sh node_modules
du -sh src-tauri/target
df -h
```

---

#### Check ports
```bash
lsof -i :1420      # Vite dev server
lsof -i :8080      # Web server
```

---

#### Check processes
```bash
ps aux | grep opcode
ps aux | grep cargo
```

---

### Common Issues

#### Issue: "cargo not found"
```bash
# Solution
source ~/.cargo/env

# Or add to ~/.zshrc or ~/.bashrc
echo 'source ~/.cargo/env' >> ~/.zshrc
exec $SHELL
```

---

#### Issue: "bun not found"
```bash
# Solution
exec $SHELL

# Or reinstall
curl -fsSL https://bun.sh/install | bash
```

---

#### Issue: "dist/ doesn't exist"
```bash
# Solution
bun run build
```

---

#### Issue: "Multiple binaries error"
```bash
# Check Cargo.toml has this line
grep "default-run" src-tauri/Cargo.toml

# Should output:
# default-run = "opcode"

# If missing, add to [package] section
```

---

#### Issue: Port 1420 in use
```bash
# Find process
lsof -i :1420

# Kill process
kill -9 <PID>

# Or change port in vite.config.ts
```

---

#### Issue: Build fails with "linker error"
```bash
# macOS: Install Xcode Command Line Tools
xcode-select --install

# Linux: Install build essentials
sudo apt-get install build-essential

# Update Rust
rustup update
```

---

#### Issue: Frontend changes not showing
```bash
# Rebuild frontend
bun run build

# Clear cache
rm -rf node_modules/.vite dist
bun run build

# Hard refresh in browser
Cmd+Shift+R (macOS)
Ctrl+Shift+R (Linux/Windows)
```

---

#### Issue: Rust changes not compiling
```bash
# Clean and rebuild
cd src-tauri
cargo clean
cargo build

# Check for syntax errors
cargo check
```

---

#### Issue: Tests failing
```bash
# Run with verbose output
cd src-tauri
cargo test -- --nocapture

# Run single test
cargo test test_name -- --nocapture

# Update dependencies
cargo update
```

---

### Performance Commands

#### Measure build time
```bash
# Frontend
time bun run build

# Backend
cd src-tauri
time cargo build
time cargo build --release

# Full workflow
time just dev
```

---

#### Profile Rust compilation
```bash
cd src-tauri
cargo build --timings
# Opens HTML report in browser
```

---

#### Check binary size
```bash
ls -lh src-tauri/target/debug/opcode
ls -lh src-tauri/target/release/opcode

# With details
du -sh src-tauri/target/debug/opcode
du -sh src-tauri/target/release/opcode
```

---

#### Analyze dependencies
```bash
cd src-tauri
cargo tree
cargo tree --duplicates
cargo tree -i serde    # Inverse dependencies
```

---

#### Benchmark builds
```bash
# Clean build time
just clean
time just build

# Incremental build time (no changes)
touch src-tauri/src/main.rs
time cargo build

# Incremental build time (with change)
echo "// comment" >> src-tauri/src/main.rs
time cargo build
```

---

### Cleanup Commands

#### Light cleanup
```bash
just clean              # Remove build artifacts
```

---

#### Deep cleanup
```bash
rm -rf node_modules dist
cd src-tauri && cargo clean
```

---

#### Nuclear cleanup
```bash
rm -rf node_modules dist bun.lockb
cd src-tauri && cargo clean
rm -rf ~/.cargo/registry/cache
rm -rf ~/.cargo/git/checkouts
```

**Warning**: Deletes all caches, requires full re-download

---

## Command Reference Table

### Build Times (Approximate)

| Command | Clean Build | Incremental Build | Output |
|---------|------------|------------------|--------|
| `bun install` | 5-10s | 1-2s | node_modules/ |
| `bun run build` | 3-4s | 2-3s | dist/ |
| `cargo build` | 19s | 1-2s | target/debug/ |
| `cargo build --release` | 19s | 2-3s | target/release/ |
| `cargo test` | 20s | 2-3s | - |
| `just dev` | 23s | 3-5s | Running app |
| `tauri build` | 30-60s | 5-10s | Installers |

---

### Disk Space Usage

| Directory | Size |
|-----------|------|
| `node_modules/` | ~500MB |
| `dist/` | ~5MB |
| `src-tauri/target/debug/` | ~2GB |
| `src-tauri/target/release/` | ~1.5GB |
| Total (full build) | ~4GB |

---

### Port Usage

| Service | Port | Purpose |
|---------|------|---------|
| Vite dev server | 1420 | Frontend development |
| Vite HMR | 1421 | Hot module replacement |
| Tauri dev server (fallback) | 1430 | Static files |
| Web server | 8080 | Browser/mobile access |

---

### Binary Outputs

| Binary | Debug Size | Release Size | Location |
|--------|-----------|--------------|----------|
| opcode | ~120MB | ~15MB | target/[debug\|release]/opcode |
| opcode-web | ~120MB | ~15MB | target/[debug\|release]/opcode-web |
| opcode_lib.dylib | ~50MB | ~10MB | target/[debug\|release]/libopcode_lib.dylib |

---

### Platform-Specific Bundles

| Platform | Formats | Location |
|----------|---------|----------|
| macOS | .app, .dmg | target/release/bundle/[macos\|dmg]/ |
| Linux | .deb, .AppImage, .rpm | target/release/bundle/[deb\|appimage\|rpm]/ |
| Windows | .msi, .exe | target/release/bundle/[msi\|nsis]/ |

---

## Environment Variables

### Tauri-specific

```bash
# Skip dev server wait
export TAURI_CLI_NO_DEV_SERVER_WAIT=1

# Dev server port
export TAURI_CLI_PORT=1430

# CI mode
export CI=1
```

---

### Rust-specific

```bash
# Increase parallelism
export CARGO_BUILD_JOBS=8

# Verbose output
export CARGO_TERM_VERBOSE=true

# Offline mode
export CARGO_NET_OFFLINE=true

# Custom target directory
export CARGO_TARGET_DIR=/path/to/target
```

---

### Bun-specific

```bash
# Use specific bun version
export BUN_VERSION=1.3.0

# Install strategy
export BUN_INSTALL_STRATEGY=auto

# Cache directory
export BUN_INSTALL_CACHE_DIR=~/.bun/install/cache
```

---

## Keyboard Shortcuts (In-App)

These are application shortcuts when running `just dev` or `tauri dev`:

| Shortcut | Action |
|----------|--------|
| Cmd+R / Ctrl+R | Reload frontend |
| Cmd+Shift+R | Hard reload |
| Cmd+Q / Ctrl+Q | Quit application |
| F12 | Open DevTools (debug mode) |

**Note**: Shortcuts configured in Tauri app, may vary

---

## Summary

This reference covers:

- **200+ commands** across 5 major tools (Bun, Just, Cargo, Tauri, NPM)
- **Complete syntax and options** for each command
- **Performance metrics** (build times, sizes)
- **Troubleshooting guides** for common issues
- **Workflow recipes** for development, testing, and deployment
- **Platform-specific** commands and outputs
- **Environment configuration** options

### Key Commands by Use Case

**Quick Start**: `just dev`
**Production Build**: `bun run tauri build`
**Testing**: `just test && bun run check`
**Mobile Access**: `just web && just ip`
**Clean Rebuild**: `just rebuild`
**Version Bump**: `./scripts/bump-version.sh 1.0.0`

### Tools Hierarchy

1. **Just** - High-level workflows (recommended for daily use)
2. **Bun** - Package management and frontend builds
3. **Tauri CLI** - Desktop app lifecycle
4. **Cargo** - Rust compilation and testing
5. **NPM Scripts** - Custom project scripts

**Recommendation**: Use `just` commands for simplicity, drop down to lower-level tools when needed.

---

*Last updated: 2025-10-20*
*Project version: 0.2.1*
*Tauri version: 2.7.1*
