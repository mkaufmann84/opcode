# Compilation Reference

Complete compilation reference for the Opcode project, covering build pipelines, optimization, caching, warnings, and troubleshooting.

## Table of Contents

- [Build Times](#build-times)
- [Build Pipeline Overview](#build-pipeline-overview)
- [Frontend Build Process](#frontend-build-process)
- [Backend Build Process](#backend-build-process)
- [Dependencies](#dependencies)
- [Build Artifacts](#build-artifacts)
- [Compiler Warnings](#compiler-warnings)
- [Build Profiles](#build-profiles)
- [Feature Flags](#feature-flags)
- [Incremental Compilation](#incremental-compilation)
- [Build Caching](#build-caching)
- [Build Optimization](#build-optimization)
- [Platform-Specific Builds](#platform-specific-builds)
- [Build Commands Reference](#build-commands-reference)
- [Troubleshooting](#troubleshooting)
- [Clean Build Procedures](#clean-build-procedures)

---

## Build Times

### Initial Build (Clean State)
- **First Rust compile**: ~19-38 seconds
  - Downloads 600+ crates from crates.io
  - Compiles 726 dependencies
  - Generates 651 build artifacts
  - Creates incremental compilation cache
- **Frontend build**: ~3-4 seconds (3.57-3.62s measured)
  - TypeScript compilation
  - Vite bundling with Rollup
  - Asset processing
  - 4616 modules transformed

### Incremental Builds
- **Rust recompile** (no changes): 1-2 seconds
- **Rust recompile** (minor changes): 2-10 seconds depending on scope
- **Frontend rebuild**: ~3-4 seconds (Vite doesn't have hot reload in this setup)

### Full Production Build
- **Tauri build** (release): Varies by platform
  - Rust compilation: 2-5 minutes (first time)
  - Asset bundling: 5-10 seconds
  - Platform bundle creation: 30 seconds - 2 minutes

---

## Build Pipeline Overview

The Opcode project uses a **two-stage build process**:

1. **Frontend Stage**: React + TypeScript → Vite → Static files in `dist/`
2. **Backend Stage**: Rust + Tauri → Native binary with embedded frontend

**Critical Note**: This is NOT a standard Tauri hot-reload setup. The frontend must be built FIRST before running the Tauri app.

### Build Flow Diagram

```
┌─────────────────────────────────────────┐
│ 1. Frontend Build (bun run build)      │
│    - TypeScript compilation (tsc)      │
│    - Vite bundling                      │
│    - Asset optimization                 │
│    → Output: dist/ directory            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 2. Backend Build (cargo build)          │
│    - Rust compilation                   │
│    - Tauri build (build.rs)             │
│    - Embed dist/ into binary            │
│    → Output: target/debug/opcode        │
└─────────────────────────────────────────┘
```

---

## Frontend Build Process

### Step-by-Step Breakdown

#### 1. TypeScript Compilation
**Tool**: `tsc` (TypeScript Compiler)
**Config**: `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noEmit": true  // Type checking only, no output
  }
}
```

**What it does**:
- Type checks all TypeScript code
- Validates React JSX syntax
- Checks path aliases (`@/*` → `./src/*`)
- Enforces strict type safety
- Does NOT emit JavaScript (handled by Vite)

**Time**: ~1-2 seconds

#### 2. Vite Bundling
**Tool**: Vite 6.0.3 with Rollup
**Config**: `vite.config.ts`

**Build Steps**:
1. **Module Resolution**: Resolves 4616 modules
2. **Tree Shaking**: Removes unused code
3. **Code Splitting**: Creates manual chunks for vendors
4. **Minification**: Minifies JavaScript and CSS
5. **Asset Processing**: Optimizes images, fonts, audio
6. **Hash Generation**: Adds content hashes to filenames

**Code Splitting Strategy**:
```javascript
manualChunks: {
  'react-vendor': ['react', 'react-dom'],
  'ui-vendor': ['@radix-ui/*'],
  'editor-vendor': ['@uiw/react-md-editor'],
  'syntax-vendor': ['react-syntax-highlighter'],
  'tauri': ['@tauri-apps/*'],
  'utils': ['date-fns', 'clsx', 'tailwind-merge']
}
```

**Time**: ~2-3 seconds

#### 3. Tailwind CSS Processing
**Tool**: Tailwind CSS 4.1.8 (via Vite plugin)

**What it does**:
- Scans all source files for Tailwind classes
- Generates minimal CSS with only used utilities
- Processes CSS through PostCSS
- Minifies output

**Output**:
- `editor-vendor-*.css`: 33.82 KB (6.04 KB gzipped)
- `index-*.css`: 102.76 KB (17.01 KB gzipped)

**Time**: Included in Vite build

#### 4. Asset Bundling
**Processed assets**:
- **Fonts**: Inter.ttf (874.71 KB) - embedded in bundle
- **Images**: PNG icons (28-100 KB)
- **Audio**: OGG notification sound (314.64 KB)
- All assets get content-hash filenames for caching

### Frontend Build Output

Total output in `dist/`:

```
dist/
├── index.html                    1.05 KB (0.42 KB gzipped)
├── assets/
│   ├── CSS Files
│   │   ├── editor-vendor-*.css   33.82 KB (6.04 KB gzipped)
│   │   └── index-*.css          102.76 KB (17.01 KB gzipped)
│   │
│   ├── JavaScript Bundles
│   │   ├── editor-vendor-*.js   1,724 KB (592 KB gzipped) ⚠️ LARGEST
│   │   ├── index-*.js            781 KB (210 KB gzipped)
│   │   ├── syntax-vendor-*.js    636 KB (228 KB gzipped)
│   │   ├── react-vendor-*.js     141 KB (45 KB gzipped)
│   │   ├── ui-vendor-*.js        109 KB (35 KB gzipped)
│   │   ├── ClaudeCodeSession-*.js 81 KB (21 KB gzipped)
│   │   ├── utils-*.js             30 KB (10 KB gzipped)
│   │   ├── tauri-*.js             15 KB (3.8 KB gzipped)
│   │   ├── AgentRunOutputViewer-*.js 14.7 KB (4.6 KB gzipped)
│   │   └── Agents-*.js            10.5 KB (3.2 KB gzipped)
│   │
│   └── Static Assets
│       ├── Inter-*.ttf           874 KB (font file)
│       ├── opcode-nfo-*.ogg      314 KB (notification sound)
│       ├── asterisk-logo-*.png   100 KB
│       └── icon-*.png             28 KB
```

**Total Size**: ~4.8 MB uncompressed, significantly smaller when gzipped
**File Count**: 18 files

---

## Backend Build Process

### Step-by-Step Breakdown

#### 1. Build Script (build.rs)
**File**: `src-tauri/build.rs`
**Purpose**: Pre-build code generation for Tauri

```rust
fn main() {
    tauri_build::build()
}
```

**What it does**:
- Generates Rust bindings for Tauri commands
- Processes icon files
- Configures platform-specific settings
- Runs BEFORE main compilation

**Time**: ~1-2 seconds

#### 2. Dependency Resolution
**Tool**: Cargo
**Dependencies**: 726 crates total

**Direct dependencies** (from Cargo.toml):
- Tauri 2 + 9 plugins (shell, dialog, fs, process, updater, etc.)
- Async runtime: tokio with "full" features
- Serialization: serde, serde_json
- Database: rusqlite with bundled SQLite
- Web server: axum + tower + tower-http
- CLI parsing: clap
- Utilities: anyhow, chrono, regex, base64, uuid, etc.

**Time**:
- First build: Downloads from crates.io (~10-15 seconds)
- Subsequent: Instant (cached in `~/.cargo/registry`)

#### 3. Rust Compilation
**Compiler**: rustc 1.90.0
**LLVM**: 20.1.8
**Target**: aarch64-apple-darwin (Apple Silicon)

**Compilation phases**:
1. **Macro expansion**: Processes derive macros, async-trait, etc.
2. **Type checking**: Validates types across all crates
3. **Monomorphization**: Generates code for generic functions
4. **LLVM optimization**: Optimizes at IR level
5. **Code generation**: Produces machine code
6. **Linking**: Links all crates into final binary

**Parallelization**:
- Default: Uses all CPU cores
- Debug build: Multiple codegen units (faster compile, slower runtime)
- Release build: `codegen-units = 1` (slower compile, faster runtime)

**Time**:
- Debug: 19-38 seconds (first), 1-2 seconds (incremental)
- Release: 2-5 minutes (first)

#### 4. Binary Types

The project builds **THREE** outputs:

1. **Library** (`libopcode_lib.{a,dylib,lib}`)
   - Crate type: lib, cdylib, staticlib
   - Shared code for both binaries
   - Size: Varies by platform

2. **Desktop App** (`opcode`)
   - Main binary (default-run)
   - Tauri GUI application
   - Size: ~65 MB (debug), ~15-20 MB (release stripped)

3. **Web Server** (`opcode-web`)
   - Standalone web server
   - For mobile/browser access
   - Size: Similar to desktop app

### Backend Build Output

**Debug build** (`target/debug/`):
```
target/debug/
├── opcode                 65 MB (unstripped, with debug symbols)
├── opcode-web             ~65 MB
├── libopcode_lib.{rlib,dylib}
├── deps/                  3.7 GB (all dependency artifacts)
├── build/                 609 MB (build script outputs)
└── incremental/           627 MB (incremental compilation cache)

Total: ~4.5 GB
```

**Release build** (`target/release/`):
- Much smaller due to `strip = true` in Cargo.toml
- Fully optimized with LTO
- No debug symbols

---

## Dependencies

### Frontend Dependencies

**Package Manager**: Bun 1.3.0 (with npm fallback support)

**Production dependencies**: 41 packages
- **React ecosystem**: react, react-dom
- **UI components**: @radix-ui/* (9 packages)
- **Markdown/Code**: @uiw/react-md-editor, react-syntax-highlighter
- **Tauri integration**: @tauri-apps/api + plugins
- **State management**: zustand
- **Forms**: react-hook-form + zod validation
- **Utilities**: date-fns, clsx, tailwind-merge, diff

**Dev dependencies**: 9 packages
- **Build tools**: @tauri-apps/cli, vite, @vitejs/plugin-react
- **Type definitions**: @types/{react,react-dom,node,sharp}
- **TypeScript**: 5.6.2
- **Image processing**: sharp

**Total installed**: ~317 MB in `node_modules/`

### Backend Dependencies

**Package Manager**: Cargo 1.90.0

**Total crates**: 726 (direct + transitive)

**Key dependency groups**:

1. **Tauri Core** (~150 crates)
   - tauri, tauri-build, tauri-runtime, tauri-utils
   - 9 official plugins
   - webkit2gtk (Linux), cocoa/objc (macOS)

2. **Async Runtime** (~50 crates)
   - tokio with all features
   - futures, async-trait
   - Runtime overhead but necessary for Tauri

3. **Web Server** (~80 crates)
   - axum (web framework)
   - tower, tower-http (middleware)
   - hyper (HTTP implementation)

4. **Database** (~20 crates)
   - rusqlite with bundled SQLite
   - No need for system SQLite

5. **Serialization** (~30 crates)
   - serde ecosystem
   - serde_json, serde_yaml

6. **Compression/Crypto** (~40 crates)
   - zstd (compression)
   - sha2 (hashing)
   - Various crypto primitives

**Cargo cache**: ~342 MB in `~/.cargo/registry/`

---

## Build Artifacts

### Development Artifacts

**Frontend** (`dist/`):
- 18 files total (HTML, JS, CSS, assets)
- 4.8 MB uncompressed
- Content-hash filenames for cache busting

**Rust Debug** (`src-tauri/target/debug/`):
- **Primary outputs**:
  - `opcode`: 65 MB main binary
  - `opcode.d`: Dependency info
  - Library artifacts

- **Dependency cache** (`deps/`): 3.7 GB
  - Compiled `.rlib` files for all dependencies
  - Shared between incremental builds

- **Build scripts** (`build/`): 609 MB
  - Output from build.rs scripts
  - Generated code, processed resources

- **Incremental cache** (`incremental/`): 627 MB
  - Enables fast incremental compilation
  - Cleared on clean build

**Total debug artifacts**: ~4.5 GB

### Production Artifacts

**Rust Release** (`src-tauri/target/release/`):
- Optimized binaries (15-20 MB after stripping)
- No incremental cache (slower build, smaller output)
- Strip debug symbols (configured in Cargo.toml)

**Bundle Outputs** (varies by platform):

**macOS**:
- `opcode.app`: Application bundle
- `opcode.dmg`: Disk image installer
- Size: ~30-40 MB

**Linux**:
- `opcode.deb`: Debian package
- `opcode.rpm`: RedHat package
- `opcode.AppImage`: Portable executable
- Size: ~25-35 MB

**Windows**:
- `opcode.msi`: MSI installer
- `opcode.exe`: Standalone executable
- Size: ~20-30 MB

### Artifact Locations Summary

```
project/
├── dist/                        # Frontend build (4.8 MB)
├── node_modules/                # NPM packages (317 MB)
├── src-tauri/
│   └── target/
│       ├── debug/               # Debug builds (4.5 GB)
│       └── release/             # Release builds + installers
└── ~/.cargo/
    ├── registry/                # Rust crate cache (342 MB)
    └── git/                     # Git dependency cache
```

---

## Compiler Warnings

### Current Warnings Summary

The codebase currently has **multiple non-critical warnings** that do not affect functionality but should be addressed for code cleanliness.

#### Rust Warnings

**Total**: ~30+ warnings across 2 categories

##### 1. Naming Convention Warnings (2 warnings)

**Issue**: `non_snake_case` - Variables using camelCase instead of snake_case

**Location**: `src/web_server.rs`

```rust
// Line 236
async fn cancel_claude_execution(Path(sessionId): Path<String>)
//                                     ^^^^^^^^^ should be: session_id

// Line 244
async fn get_claude_session_output(Path(sessionId): Path<String>)
//                                       ^^^^^^^^^ should be: session_id
```

**Fix**: Rename to snake_case:
```rust
async fn cancel_claude_execution(Path(session_id): Path<String>)
async fn get_claude_session_output(Path(session_id): Path<String>)
```

**Impact**: None - purely stylistic

##### 2. Dead Code Warnings (~28+ warnings)

**Issue**: `dead_code` - Unused structs, fields, and functions

**Major occurrences**:

**Checkpoint System** (`src/checkpoint/mod.rs`):
- Unused structs: `FileSnapshot`, `CheckpointDiff`, `FileDiff`
- Unused fields in `FileTracker`, `FileState`, `CheckpointPaths`
- Unused methods in `SessionTimeline` implementation

**Checkpoint Manager** (`src/checkpoint/manager.rs`):
- Most methods never called (checkpoint feature incomplete)
- Unused fields in `CheckpointManager` struct
- 17+ unused associated functions

**Binary Detection** (`src/claude_binary.rs`):
- `find_claude_binary()` - duplicate/unused
- `select_best_installation()` - unused
- `create_command_with_env()` - unused

**Agent System** (`src/commands/agents.rs`):
- `AgentExport`, `AgentData`, `AgentDb` structs unused
- `from_jsonl()` method unused
- `read_session_jsonl()` function unused

**Why these exist**:
- **Checkpoint system**: Partially implemented feature
- **Agent export**: Future functionality
- **Binary detection**: Legacy code or platform-specific

**Fix options**:
1. **Implement features**: Complete checkpoint/agent features
2. **Add `#[allow(dead_code)]`**: If planned for future
3. **Remove code**: If truly unnecessary
4. **Make conditional**: Use `#[cfg(feature = "...")]`

**Recommended approach**:
```rust
// For incomplete features
#[allow(dead_code)]
pub struct FileSnapshot { ... }

// For platform-specific code
#[cfg(target_os = "macos")]
fn macos_specific_function() { ... }

// For truly unused code
// DELETE IT
```

#### TypeScript Warnings

**Status**: No TypeScript compilation warnings
- Strict mode enabled
- All types validate correctly
- `tsc --noEmit` passes cleanly

### Warning Suppression

To suppress warnings during build (not recommended for long-term):

**Rust**:
```bash
# Suppress specific warnings
RUSTFLAGS="-A dead_code" cargo build

# Suppress all warnings
cargo build 2>&1 | grep -v "warning:"
```

**TypeScript**:
```bash
# Skip type checking (not recommended)
vite build
```

---

## Build Profiles

### Debug Profile (Default)

**Activated by**: `cargo build`, `cargo run`, `tauri dev`

**Configuration** (Cargo defaults):
```toml
[profile.dev]
opt-level = 0              # No optimization
debug = true               # Include debug symbols
split-debuginfo = "..."    # Platform-specific
debug-assertions = true    # Enable debug_assert!
overflow-checks = true     # Check integer overflow
lto = false                # No link-time optimization
panic = "unwind"           # Panic unwinds stack
incremental = true         # Enable incremental compilation
codegen-units = 256        # Parallel codegen (faster compile)
rpath = false              # No rpath
```

**Characteristics**:
- **Build time**: Fast (1-2 seconds incremental)
- **Binary size**: Large (~65 MB)
- **Runtime speed**: Slow (~10-100x slower than release)
- **Debug info**: Full symbols, line numbers
- **Optimizations**: None
- **Use case**: Active development, debugging

### Release Profile

**Activated by**: `cargo build --release`, `tauri build`

**Configuration** (from `Cargo.toml`):
```toml
[profile.release]
opt-level = "z"            # Optimize for size
lto = true                 # Link-time optimization
codegen-units = 1          # Single codegen unit (better optimization)
strip = true               # Strip debug symbols
```

**Additional defaults**:
- `debug = false` - No debug info
- `debug-assertions = false` - Disable assertions
- `overflow-checks = false` - No overflow checks
- `panic = "unwind"` - Can be changed to "abort"
- `incremental = false` - No incremental (full rebuild)

**Characteristics**:
- **Build time**: Very slow (2-5 minutes full build)
- **Binary size**: Small (~15-20 MB after strip)
- **Runtime speed**: Maximum performance
- **Debug info**: None (stripped)
- **Optimizations**: Aggressive size optimization
- **Use case**: Production releases, distribution

**Why `opt-level = "z"`?**:
- Desktop apps benefit from smaller download size
- Tauri embeds entire web UI in binary
- Slight speed tradeoff acceptable
- Alternative: `opt-level = "3"` for max speed

**LTO (Link-Time Optimization)**:
- Enables cross-crate inlining
- Removes unused code globally
- Significantly reduces binary size
- Increases compile time by ~50-100%

**Single codegen unit**:
- Better optimization (more context for LLVM)
- Slower compilation (no parallelization)
- Typical 10-20% size reduction

### Test Profile

**Activated by**: `cargo test`

**Configuration**: Similar to dev, with test-specific settings

### Benchmark Profile

**Activated by**: `cargo bench`

**Configuration**: Similar to release, optimized for benchmarking

### Custom Profiles

You can define custom profiles in `Cargo.toml`:

```toml
[profile.release-with-debug]
inherits = "release"
debug = true
strip = false
```

Then use: `cargo build --profile release-with-debug`

---

## Feature Flags

### Cargo Features

**Defined in** `Cargo.toml`:

```toml
[features]
custom-protocol = ["tauri/custom-protocol"]
```

#### `custom-protocol` Feature

**Purpose**: Required for production builds without dev server

**What it enables**:
- Uses `tauri://` custom protocol for loading assets
- Bundles frontend files into binary
- Required for distributed apps

**Activation**:
- **Automatic**: Enabled by `tauri build`
- **Manual**: `cargo build --features custom-protocol`

**When NOT to use**:
- Development with `tauri dev` (uses localhost)
- Running with `--dev` flag

### Tauri Feature Flags

**Enabled features** (from dependencies):

**Core Tauri**:
```toml
tauri = {
  version = "2",
  features = [
    "macos-private-api",  # macOS window effects
    "protocol-asset",     # Asset protocol support
    "tray-icon",          # System tray
    "image-png"           # PNG image support
  ]
}
```

**Plugin features**: All plugins auto-enabled
- tauri-plugin-shell
- tauri-plugin-dialog
- tauri-plugin-fs
- etc.

**Platform-specific features**:
```toml
[target.'cfg(target_os = "macos")'.dependencies]
tauri = { version = "2", features = ["macos-private-api"] }
```

### Frontend Feature Flags

No compile-time feature flags, but environment-based configuration:

**Build environment**:
```bash
NODE_ENV=production    # Enables production optimizations
TAURI_DEV_HOST=...     # Custom dev host
```

**Vite mode**:
- Development: `vite dev` (HMR, source maps)
- Production: `vite build` (minification, tree-shaking)

---

## Incremental Compilation

### How It Works

Rust's incremental compilation caches intermediate results to speed up rebuilds.

**Cache location**: `target/debug/incremental/` (~627 MB)

**What's cached**:
- **HIR** (High-level IR): Type-checked AST
- **MIR** (Mid-level IR): Optimized representation
- **LLVM IR**: Pre-codegen state
- **Query results**: Type checking, trait resolution
- **Codegen units**: Partially compiled code

**When cache is used**:
1. You modify a file
2. Cargo detects changes via timestamps/hashes
3. Only affected modules recompile
4. Cached results reused for unchanged code

**Effectiveness**:
- Tiny change: 1-2 seconds
- Medium change: 5-10 seconds
- Large refactor: 20-30 seconds
- Dependency change: Full rebuild

### Incremental Compilation Settings

**Debug profile** (incremental enabled):
```toml
[profile.dev]
incremental = true
```

**Release profile** (incremental disabled):
```toml
[profile.release]
incremental = false  # Default
```

**Why disabled in release?**:
- Incremental builds are less optimized
- Release builds should be reproducible
- Cache invalidation is complex

### Cache Management

**View cache size**:
```bash
du -sh target/debug/incremental
# Output: 627M
```

**Clear cache**:
```bash
cargo clean -p opcode  # Clear only this project
cargo clean            # Clear everything
```

**When to clear**:
- Mysterious compile errors
- After toolchain update
- If cache grows too large (>1 GB)
- Before committing Cargo.lock changes

### Performance Tips

**Maximize incremental benefits**:
1. **Keep changes small**: Edit one module at a time
2. **Avoid dependency changes**: Don't modify Cargo.toml frequently
3. **Use cargo check**: Faster than `cargo build` for checking
4. **Modularize code**: Smaller modules = better cache granularity

**Check what's rebuilding**:
```bash
cargo build -v | grep Compiling
```

---

## Build Caching

### Cargo Crate Cache

**Location**: `~/.cargo/registry/` (~342 MB)

**What's cached**:
- **registry/index**: Crates.io index (package metadata)
- **registry/cache**: Downloaded `.crate` files
- **registry/src**: Extracted source code
- **git/**: Git dependencies

**How it works**:
1. First build downloads crates from crates.io
2. Stored in global cache (shared across projects)
3. Subsequent builds use cached versions
4. Updates only on `cargo update`

**Cache management**:
```bash
# View cache size
du -sh ~/.cargo/registry

# Clean old cache (requires cargo-cache)
cargo install cargo-cache
cargo cache --autoclean

# Manual cleanup
rm -rf ~/.cargo/registry/cache
cargo build  # Re-downloads
```

### Frontend Caching

**NPM/Bun cache**:
- **Location**: `node_modules/` (project-local)
- **Size**: ~317 MB
- **Shared**: No (per-project)

**Vite build cache**:
- **Location**: `node_modules/.vite/`
- **Purpose**: Pre-bundling dependencies
- **Effect**: Faster dev server startup

**Browser cache**:
- Content-hash filenames enable long-term caching
- Example: `index-DqqjNpor.js` (hash changes on content change)

### CI/CD Caching Strategies

**For GitHub Actions / CI**:

```yaml
- uses: actions/cache@v3
  with:
    path: |
      ~/.cargo/registry
      ~/.cargo/git
      src-tauri/target
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}

- uses: actions/cache@v3
  with:
    path: node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/bun.lockb') }}
```

**Cache invalidation**:
- Cargo cache: When `Cargo.lock` changes
- Node cache: When `bun.lockb` changes
- Incremental: Not cached in CI (unreliable across runs)

---

## Build Optimization

### Compile Time Optimization

#### 1. Use `cargo check` During Development

```bash
cargo check      # Type check only (5-10x faster)
cargo build      # Full compilation
```

**When to use each**:
- `check`: Validating code changes
- `build`: Actually running the app

#### 2. Reduce Codegen Units in Debug

Trade faster runtime for slightly slower compilation:

```toml
[profile.dev]
codegen-units = 16  # Default is 256
```

#### 3. Enable Parallel Frontend Builds

Already configured - Vite uses all CPU cores.

#### 4. Use Cargo Workspaces

For very large projects, split into multiple crates:

```toml
[workspace]
members = ["src-tauri", "shared-lib"]
```

Not needed for Opcode currently.

#### 5. Optimize Dependencies

**Replace slow dependencies**:
- Use `cargo tree --duplicates` to find duplicate deps
- Use `cargo bloat` to find large dependencies

**Example optimization**:
```toml
# Pin to avoid recompilation
image = "=0.25.1"  # Exact version (already in Cargo.toml)
```

### Binary Size Optimization

Already heavily optimized in release profile:

```toml
[profile.release]
opt-level = "z"      # Optimize for size (already set)
lto = true           # Link-time optimization (already set)
strip = true         # Remove symbols (already set)
codegen-units = 1    # Better optimization (already set)
```

**Additional optimizations** (optional):

```toml
[profile.release]
panic = "abort"      # Don't unwind, saves ~100KB
opt-level = "s"      # Alternative size optimization
```

**Frontend size optimization**:
- Already using code splitting
- Already using tree-shaking
- Already minifying

**To reduce further**:
1. Lazy load routes
2. Remove unused dependencies
3. Use dynamic imports
4. Compress with Brotli/Gzip

### Runtime Performance Optimization

**Already optimized**:
- Release builds use LTO
- Single codegen unit
- LLVM optimization level "z"

**Further optimizations**:

```toml
[profile.release]
opt-level = "3"      # Max speed (slight size increase)
lto = "fat"          # More aggressive LTO
```

**CPU-specific optimization**:
```bash
RUSTFLAGS="-C target-cpu=native" cargo build --release
```

**Warning**: Binary won't work on older CPUs.

### Build Performance Benchmarks

**Measured times** (Apple Silicon M-series):

| Operation | Time | Notes |
|-----------|------|-------|
| `bun install` | 9 seconds | First time, 409 packages |
| `bun run build` | 3.6-7.9 seconds | Frontend only |
| `tsc --noEmit` | 1-2 seconds | Type check only |
| `cargo check` | 2-5 seconds | Incremental |
| `cargo build` | 1-2 seconds | Incremental, no changes |
| `cargo build` | 19-38 seconds | First time |
| `cargo build --release` | 2-5 minutes | Full optimization |
| `tauri build` | 3-7 minutes | Full release + bundle |

**Full clean build** (worst case):
```
bun install           9s
bun run build         4s
cargo build --release 180s
Bundle creation       30s
---------------------------------
Total:                223s (~3.7 minutes)
```

---

## Platform-Specific Builds

### macOS Builds

**Target**: `aarch64-apple-darwin` (Apple Silicon) or `x86_64-apple-darwin` (Intel)

**Platform-specific dependencies**:
```toml
[target.'cfg(target_os = "macos")'.dependencies]
tauri = { version = "2", features = ["macos-private-api"] }
window-vibrancy = "0.5"    # Translucent windows
cocoa = "0.26"             # macOS frameworks
objc = "0.2"               # Objective-C runtime
```

**Features**:
- Translucent window backgrounds
- macOS-native vibrancy effects
- Private API access for window effects

**Bundle configuration** (`tauri.conf.json`):
```json
"macOS": {
  "minimumSystemVersion": "10.15",
  "frameworks": [],
  "entitlements": "entitlements.plist",
  "dmg": {
    "windowSize": { "width": 540, "height": 380 },
    "appPosition": { "x": 140, "y": 200 },
    "applicationFolderPosition": { "x": 400, "y": 200 }
  }
}
```

**Output**:
- `opcode.app` - Application bundle
- `opcode.dmg` - Disk image installer

**Code signing**:
```bash
# Development
tauri build

# Production (requires Apple Developer account)
tauri build --target aarch64-apple-darwin
# Sign with your identity
codesign --force --deep --sign "Developer ID Application: ..." opcode.app
```

### Linux Builds

**Target**: `x86_64-unknown-linux-gnu` or `aarch64-unknown-linux-gnu`

**Cross-compilation config** (`.cargo/config.toml`):
```toml
[target.aarch64-unknown-linux-gnu]
linker = "aarch64-linux-gnu-gcc"

[env]
PKG_CONFIG_ALLOW_CROSS = "1"
```

**Platform dependencies**:
```json
"linux": {
  "deb": {
    "depends": ["libwebkit2gtk-4.1-0", "libgtk-3-0"]
  },
  "appimage": {
    "bundleMediaFramework": true
  }
}
```

**Output formats**:
- `.deb` - Debian/Ubuntu package
- `.rpm` - RedHat/Fedora package
- `.AppImage` - Portable executable

**Building on macOS for Linux** (cross-compilation):
```bash
# Install cross-compilation tools
brew install filosottile/musl-cross/musl-cross

# Build
cargo build --target x86_64-unknown-linux-gnu
```

### Windows Builds

**Target**: `x86_64-pc-windows-msvc` or `x86_64-pc-windows-gnu`

**Output formats**:
- `.msi` - MSI installer
- `.exe` - Standalone executable

**Building on macOS for Windows**:
```bash
# Install mingw-w64
brew install mingw-w64

# Add target
rustup target add x86_64-pc-windows-gnu

# Build
cargo build --target x86_64-pc-windows-gnu
```

**Note**: Cross-compiling to Windows from macOS/Linux is complex. Use CI or Windows VM for production builds.

### Universal Binary (macOS)

Build for both Intel and Apple Silicon:

```bash
rustup target add x86_64-apple-darwin
rustup target add aarch64-apple-darwin

# Build both
cargo build --release --target x86_64-apple-darwin
cargo build --release --target aarch64-apple-darwin

# Create universal binary
lipo -create \
  target/x86_64-apple-darwin/release/opcode \
  target/aarch64-apple-darwin/release/opcode \
  -output opcode-universal
```

### Cross-Compilation Summary

| From → To | Difficulty | Recommended Approach |
|-----------|------------|----------------------|
| macOS → macOS | Easy | Native build |
| macOS → Linux | Medium | Cross-compile or Docker |
| macOS → Windows | Hard | Use GitHub Actions |
| Linux → Linux | Easy | Native build |
| Linux → macOS | Hard | Use GitHub Actions |
| Linux → Windows | Medium | Cross-compile (mingw) |
| Windows → Windows | Easy | Native build |
| Windows → macOS | Very Hard | Use GitHub Actions |
| Windows → Linux | Medium | WSL or Docker |

**Best practice**: Use GitHub Actions for multi-platform releases.

---

## Build Commands Reference

### Frontend Commands

```bash
# Install dependencies
bun install              # Installs to node_modules/

# Build frontend
bun run build            # tsc + vite build → dist/

# Type check only
bun run tsc --noEmit     # No output, just validation

# Development server (NOT USED in this project)
bun run dev              # Vite dev server on :1420

# Preview production build
bun run preview          # Serve dist/ locally
```

### Backend Commands

```bash
# Check code (fast, no binary)
cargo check              # Type check only

# Build debug binary
cargo build              # → target/debug/opcode

# Build release binary
cargo build --release    # → target/release/opcode

# Run debug binary
cargo run                # Build + run opcode

# Run specific binary
cargo run --bin opcode       # Desktop app
cargo run --bin opcode-web   # Web server

# Run with arguments
cargo run --bin opcode-web -- --port 8080

# Test
cargo test               # Run all tests

# Format code
cargo fmt                # Auto-format Rust code

# Lint
cargo clippy             # Run linter
```

### Tauri Commands

```bash
# Development (frontend must be pre-built)
bun run tauri dev        # Run desktop app in dev mode

# Production build
bun run tauri build      # Full release build + bundles

# Build specific bundle
bun run tauri build --bundles dmg        # macOS DMG only
bun run tauri build --bundles deb        # Linux DEB only
bun run tauri build --bundles msi        # Windows MSI only

# Build for specific target
bun run tauri build --target aarch64-apple-darwin
```

### Just Commands

Convenience wrapper around common tasks:

```bash
# List all commands
just

# Development
just dev                 # Build frontend + run app
just quick               # Same as dev

# Build steps
just install             # npm install
just build-frontend      # Build React app
just build-backend       # cargo build
just build               # All of the above

# Run modes
just run                 # Build frontend + cargo run
just run-release         # Release build + run
just web                 # Run web server (port 8080)
just web-port 3000       # Custom port

# Maintenance
just clean               # Remove all build artifacts
just test                # cargo test
just fmt                 # cargo fmt
just check               # cargo check

# Utilities
just ip                  # Show local IP for phone access
just info                # Show project information
```

### Combined Workflows

**Full development cycle**:
```bash
# One-time setup
bun install

# Development loop
bun run build            # Rebuild frontend
cargo run                # Run app

# Or use just
just dev                 # Does both
```

**Full production build**:
```bash
# Clean build from scratch
bun install
bun run build
cargo build --release
bun run tauri build      # Creates installers
```

**Quick iteration**:
```bash
# Make code changes, then:
bun run build && cargo run

# Or:
just quick
```

---

## Troubleshooting

### Common Build Errors

#### 1. "frontendDist doesn't exist"

**Error**:
```
The `frontendDist` configuration is set to "../dist" but this path doesn't exist
```

**Cause**: Frontend not built before running Tauri

**Fix**:
```bash
bun run build
bun run tauri dev
```

#### 2. "could not determine which binary to run"

**Error**:
```
error: `cargo run` could not determine which binary to run.
Use the `--bin` option to specify a binary, or the `default-run` manifest key.
available binaries: opcode, opcode-web
```

**Cause**: Missing `default-run` in Cargo.toml (already fixed)

**Fix**: Already fixed in `Cargo.toml`:
```toml
[package]
default-run = "opcode"
```

#### 3. "No such file or directory (cargo)"

**Error**:
```
failed to get cargo metadata: No such file or directory (os error 2)
```

**Cause**: Cargo not in PATH

**Fix**:
```bash
source "$HOME/.cargo/env"
bun run tauri dev
```

Or add to `~/.zshrc`:
```bash
source "$HOME/.cargo/env"
```

#### 4. Linking Errors on Linux

**Error**:
```
error: linking with `cc` failed: exit status: 1
= note: /usr/bin/ld: cannot find -lwebkit2gtk-4.1
```

**Cause**: Missing system dependencies

**Fix**:
```bash
# Debian/Ubuntu
sudo apt install libwebkit2gtk-4.1-dev libgtk-3-dev

# Fedora
sudo dnf install webkit2gtk4.1-devel gtk3-devel
```

#### 5. "image requires edition2024"

**Error**:
```
error: package `image v0.26.0` cannot be built because it requires edition2024
```

**Cause**: Dependency requires newer Rust edition

**Fix**: Already fixed by pinning:
```toml
image = "=0.25.1"
```

#### 6. Incremental Compilation Errors

**Error**:
```
error: internal compiler error: ... incremental compilation
```

**Cause**: Corrupted incremental cache

**Fix**:
```bash
cargo clean
cargo build
```

### Build Performance Issues

#### Slow Compilation

**Symptoms**: Builds taking >5 minutes

**Diagnosis**:
```bash
# Check what's compiling
cargo build -v | grep Compiling

# Profile build times
cargo build --timings
# Open target/cargo-timings/cargo-timing.html
```

**Solutions**:
1. Use `cargo check` instead of `cargo build`
2. Reduce dependencies (check with `cargo tree`)
3. Enable sccache:
   ```bash
   cargo install sccache
   export RUSTC_WRAPPER=sccache
   ```

#### Disk Space Issues

**Symptoms**: "No space left on device"

**Check usage**:
```bash
du -sh target
du -sh ~/.cargo/registry
du -sh node_modules
```

**Solutions**:
```bash
# Clean old build artifacts
cargo clean

# Clean cargo cache
cargo install cargo-cache
cargo cache --autoclean

# Clean frontend
rm -rf node_modules dist
bun install
```

### Runtime Issues After Build

#### Binary Crashes Immediately

**Check dependencies**:
```bash
# macOS
otool -L target/release/opcode

# Linux
ldd target/release/opcode
```

**Common causes**:
- Missing system libraries
- Wrong glibc version (Linux)
- Code signing issues (macOS)

#### Web Server Port Already in Use

**Error**:
```
Error: Address already in use (os error 48)
```

**Fix**:
```bash
# Find process using port 8080
lsof -i :8080

# Kill it
kill -9 <PID>

# Or use different port
cargo run --bin opcode-web -- --port 3000
```

---

## Clean Build Procedures

### Full Clean Build

Remove all artifacts and rebuild from scratch:

```bash
# Clean everything
cargo clean              # Remove target/
rm -rf dist              # Remove frontend build
rm -rf node_modules      # Remove dependencies
rm -rf ~/.cargo/registry # Remove cargo cache (optional)

# Rebuild
bun install              # Reinstall frontend deps
bun run build            # Build frontend
cargo build              # Build backend
```

**When to use**:
- Mysterious build errors
- After major dependency updates
- Before releasing
- After toolchain updates

### Partial Clean Procedures

#### Clean Only Rust

```bash
cargo clean              # Remove all Rust artifacts

# Or clean specific package
cargo clean -p opcode

# Or clean specific target
cargo clean --release
```

#### Clean Only Frontend

```bash
rm -rf dist node_modules
bun install
bun run build
```

#### Clean Only Incremental Cache

```bash
rm -rf target/debug/incremental
cargo build
```

Useful when incremental compilation is misbehaving.

#### Clean Only Dependencies

```bash
rm -rf target/debug/deps target/release/deps
cargo build
```

Forces recompilation of all dependencies but keeps incremental cache.

### Automated Clean Scripts

Add to `package.json`:
```json
"scripts": {
  "clean": "rm -rf dist target node_modules",
  "clean:build": "rm -rf dist target && bun install && bun run build"
}
```

Or use Just:
```bash
just clean      # Already defined in justfile
just rebuild    # Clean + build + run
```

### CI/CD Clean Builds

Always use clean builds in CI:

```yaml
- name: Clean build
  run: |
    cargo clean
    rm -rf dist
    bun install
    bun run build
    cargo build --release
```

Don't cache `target/` in release builds (only cache cargo registry).

---

## Additional Resources

### Documentation
- [Cargo Book](https://doc.rust-lang.org/cargo/) - Cargo reference
- [Tauri Docs](https://tauri.app/) - Tauri framework
- [Vite Docs](https://vitejs.dev/) - Vite bundler
- [Rust Performance Book](https://nnethercote.github.io/perf-book/) - Optimization guide

### Tools

**Profiling**:
```bash
cargo install cargo-bloat     # Analyze binary size
cargo install cargo-tree      # Analyze dependencies
cargo install cargo-outdated  # Check for updates
cargo install cargo-audit     # Security audit
```

**Build analysis**:
```bash
cargo build --timings         # Build time breakdown
cargo tree --duplicates       # Find duplicate deps
cargo bloat --release         # What's taking space
```

**Benchmarking**:
```bash
hyperfine 'bun run build'            # Benchmark frontend
hyperfine 'cargo build --quiet'      # Benchmark backend
```

---

## Summary

This comprehensive compilation reference documents:

- **Build pipelines**: 2-stage frontend → backend process
- **Timing**: 3.6s frontend, 1-38s backend (incremental vs cold)
- **Dependencies**: 726 Rust crates, 41 npm packages
- **Artifacts**: 4.8 MB frontend, 4.5 GB debug, 15-20 MB release
- **Warnings**: 2 naming, 28+ dead code (non-critical)
- **Profiles**: Debug (fast build) vs Release (optimized)
- **Features**: `custom-protocol` for production
- **Caching**: 627 MB incremental, 342 MB cargo registry
- **Optimization**: Already aggressive in release profile
- **Platforms**: macOS (native), Linux/Windows (cross-compile)
- **Commands**: 20+ build commands via cargo/bun/just/tauri

The build system is already well-optimized with intelligent code splitting, LTO, stripping, and size optimization. Main improvement areas are fixing dead code warnings and completing the checkpoint feature implementation.
