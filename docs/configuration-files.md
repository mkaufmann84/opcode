# Configuration Files Reference

This document provides a comprehensive reference for all configuration files in the Opcode project. Every configuration option is explained with its purpose, default values, when to modify it, and the impact of changes.

---

## Table of Contents

1. [Tauri Configuration](#tauri-configuration)
2. [Rust/Cargo Configuration](#rustcargo-configuration)
3. [Frontend Configuration](#frontend-configuration)
4. [TypeScript Configuration](#typescript-configuration)
5. [Build System Configuration](#build-system-configuration)
6. [macOS-Specific Configuration](#macos-specific-configuration)
7. [Security & Permissions](#security--permissions)
8. [Git Configuration](#git-configuration)
9. [Environment Variables](#environment-variables)
10. [Configuration Interdependencies](#configuration-interdependencies)
11. [Troubleshooting Misconfigurations](#troubleshooting-misconfigurations)

---

## Tauri Configuration

### Location
`/Users/max/local/opcode/src-tauri/tauri.conf.json`

### Complete Structure

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "opcode",
  "version": "0.2.1",
  "identifier": "opcode.asterisk.so",
  "build": { ... },
  "app": { ... },
  "plugins": { ... },
  "bundle": { ... }
}
```

### Root Level Fields

#### `$schema`
- **Value**: `"https://schema.tauri.app/config/2"`
- **Purpose**: Enables IDE autocomplete and validation for Tauri 2 config
- **When to Change**: Only when upgrading to a new major Tauri version
- **Impact**: No runtime impact, only affects editor support

#### `productName`
- **Value**: `"opcode"`
- **Purpose**: The human-readable name of the application
- **When to Change**: When rebranding or renaming the application
- **Impact**: Affects window titles, installer names, and macOS menu bar
- **Related**: Must match `CFBundleName` in Info.plist

#### `version`
- **Value**: `"0.2.1"`
- **Purpose**: Application version for releases and updates
- **When to Change**: Before each release (follow semantic versioning)
- **Impact**: Affects bundle identifiers, update system, and About dialog
- **Related**: Must match `version` in Cargo.toml and package.json

#### `identifier`
- **Value**: `"opcode.asterisk.so"`
- **Purpose**: Unique reverse-domain identifier for the application
- **When to Change**: NEVER after first release (breaks updates and settings)
- **Impact**: Determines app data storage location, bundle ID on macOS
- **Format**: Reverse domain notation (com.company.app)
- **Security**: Must be unique to avoid conflicts with other apps

### Build Configuration

```json
"build": {
  "beforeDevCommand": "",
  "beforeBuildCommand": "bun run build",
  "frontendDist": "../dist"
}
```

#### `beforeDevCommand`
- **Value**: `""` (intentionally empty)
- **Default**: Usually `"npm run dev"` or similar
- **Purpose**: Command to run before starting Tauri dev server
- **Why Empty**: This project uses a build-first workflow, not hot-reload
- **Workflow**: Run `bun run build` manually, THEN `tauri dev`
- **When to Change**: If switching to hot-reload dev workflow
- **Impact**: If set, would run a dev server before Tauri starts

#### `beforeBuildCommand`
- **Value**: `"bun run build"`
- **Purpose**: Command to build frontend before production bundle
- **When to Change**: If switching package managers (npm, yarn, pnpm)
- **Impact**: Production builds will fail if this doesn't generate dist/
- **Related**: Must output to directory specified in `frontendDist`

#### `frontendDist`
- **Value**: `"../dist"`
- **Purpose**: Path to compiled frontend assets (relative to src-tauri/)
- **When to Change**: If changing Vite build output directory
- **Impact**: Tauri won't find frontend if path is wrong
- **Related**: Must match `build.outDir` in vite.config.ts (default is "dist")

### App Configuration

```json
"app": {
  "macOSPrivateApi": true,
  "windows": [...],
  "security": {...}
}
```

#### `macOSPrivateApi`
- **Value**: `true`
- **Default**: `false`
- **Purpose**: Enables macOS private APIs for enhanced window effects
- **When to Enable**: For transparency, vibrancy, and visual effects
- **Impact**: Requires additional entitlements, may break on macOS updates
- **Security**: Use with caution, Apple may reject App Store submissions
- **Related**: Requires window-vibrancy dependency in Cargo.toml

#### Windows Configuration

```json
"windows": [
  {
    "title": "opcode",
    "width": 800,
    "height": 600,
    "decorations": false,
    "transparent": true,
    "shadow": true,
    "center": true,
    "resizable": true,
    "alwaysOnTop": false
  }
]
```

**Field Reference:**

| Field | Value | Purpose | When to Change |
|-------|-------|---------|----------------|
| `title` | `"opcode"` | Initial window title | When changing app branding |
| `width` | `800` | Initial window width (px) | To change default size |
| `height` | `600` | Initial window height (px) | To change default size |
| `decorations` | `false` | Hide native title bar | For custom title bars only |
| `transparent` | `true` | Enable window transparency | For rounded corners/effects |
| `shadow` | `true` | Show window drop shadow | If transparency is disabled |
| `center` | `true` | Center window on screen | For specific positioning |
| `resizable` | `true` | Allow window resize | For fixed-size windows |
| `alwaysOnTop` | `false` | Keep above other windows | For utility/tool windows |

**Advanced Window Options (Not Currently Used):**

```json
{
  "minWidth": 400,
  "minHeight": 300,
  "maxWidth": 1920,
  "maxHeight": 1080,
  "fullscreen": false,
  "visible": true,
  "focus": true,
  "skipTaskbar": false,
  "titleBarStyle": "Overlay",  // macOS only
  "hiddenTitle": true,         // macOS only
  "fileDropEnabled": true,
  "url": "index.html"
}
```

#### Security Configuration

```json
"security": {
  "csp": "default-src 'self'; img-src 'self' asset: https://asset.localhost blob: data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-eval' https://app.posthog.com https://*.posthog.com https://*.i.posthog.com https://*.assets.i.posthog.com; connect-src 'self' ipc: https://ipc.localhost https://app.posthog.com https://*.posthog.com https://*.i.posthog.com",
  "assetProtocol": {
    "enable": true,
    "scope": ["**"]
  }
}
```

**Content Security Policy (CSP) Breakdown:**

| Directive | Allowed Sources | Purpose |
|-----------|----------------|---------|
| `default-src` | `'self'` | Default fallback: only load from app |
| `img-src` | `'self'`, `asset:`, `blob:`, `data:` | Load images from app, assets, and data URIs |
| `style-src` | `'self'`, `'unsafe-inline'` | Allow inline styles (required for React) |
| `script-src` | `'self'`, `'unsafe-eval'`, PostHog domains | Allow app scripts and analytics |
| `connect-src` | `'self'`, `ipc:`, PostHog domains | Allow IPC and analytics API calls |

**When to Modify CSP:**

- **Adding external APIs**: Add domain to `connect-src`
- **Embedding images/videos**: Add domain to `img-src` or `media-src`
- **Third-party scripts**: Add domain to `script-src` (security risk!)
- **Fonts**: Add `font-src` directive with CDN domains

**Security Warnings:**

- `'unsafe-inline'` in style-src: Required for CSS-in-JS, potential XSS risk
- `'unsafe-eval'` in script-src: Required for some JS features, major XSS risk
- Minimize use of `unsafe-*` directives in production

**Asset Protocol:**

```json
"assetProtocol": {
  "enable": true,
  "scope": ["**"]
}
```

- **enable**: Activates `asset://` protocol for loading local files
- **scope**: `["**"]` allows all files (DANGEROUS - consider restricting)
- **Better scope**: `["$RESOURCE/*", "$APP/*"]` for production
- **Purpose**: Load images, fonts, and media from app bundle

### Plugins Configuration

```json
"plugins": {
  "fs": {
    "scope": ["$HOME/**"],
    "allow": [
      "readFile", "writeFile", "readDir", "copyFile",
      "createDir", "removeDir", "removeFile", "renameFile", "exists"
    ]
  },
  "shell": {
    "open": true
  }
}
```

#### Filesystem Plugin

**Scope:**
- **Value**: `["$HOME/**"]`
- **Purpose**: Restricts file operations to user's home directory
- **Security**: Prevents access to system files
- **Variables**: `$HOME`, `$RESOURCE`, `$APP`, `$TEMP`, `$DESKTOP`, etc.
- **Example restrictive scope**:
  ```json
  "scope": [
    "$HOME/.claude/**",
    "$HOME/Documents/**"
  ]
  ```

**Allowed Operations:**
- `readFile`: Read file contents
- `writeFile`: Create/overwrite files
- `readDir`: List directory contents
- `copyFile`: Duplicate files
- `createDir`: Create directories
- `removeDir`: Delete directories
- `removeFile`: Delete files
- `renameFile`: Rename/move files
- `exists`: Check if path exists

**Security Considerations:**
- Each operation requires explicit permission
- Scope prevents directory traversal attacks
- Remove unused operations in production
- Never scope to `["**"]` (full system access)

#### Shell Plugin

```json
"shell": {
  "open": true
}
```

- **open**: Allows `shell.open()` to open URLs/files in default apps
- **Purpose**: Open links in browser, files in default editor
- **Security**: Limited to opening, not executing arbitrary commands
- **Alternative**: Use `shell:allow-execute` for command execution

**Advanced Shell Configuration:**

```json
"shell": {
  "open": true,
  "scope": [
    {
      "name": "run-claude",
      "cmd": "claude",
      "args": true,
      "sidecar": false
    }
  ]
}
```

### Bundle Configuration

```json
"bundle": {
  "active": true,
  "targets": ["deb", "rpm", "appimage", "app", "dmg"],
  "icon": [...],
  "resources": [],
  "externalBin": [],
  "copyright": "© 2025 Asterisk. All rights reserved.",
  "category": "DeveloperTool",
  "shortDescription": "GUI app and Toolkit for Claude Code",
  "longDescription": "..."
}
```

#### Bundle Fields Reference

| Field | Value | Purpose | Platform |
|-------|-------|---------|----------|
| `active` | `true` | Enable bundler | All |
| `targets` | Array | Installer formats to build | Varies |
| `copyright` | String | Copyright notice | All |
| `category` | `"DeveloperTool"` | App category | Linux/macOS |
| `shortDescription` | String | One-line description | Linux |
| `longDescription` | String | Full description | Linux/macOS |

**Bundle Targets:**

| Target | Platform | Output |
|--------|----------|--------|
| `deb` | Linux (Debian/Ubuntu) | .deb package |
| `rpm` | Linux (Fedora/RHEL) | .rpm package |
| `appimage` | Linux (Universal) | .AppImage executable |
| `app` | macOS | .app bundle |
| `dmg` | macOS | .dmg installer |
| `msi` | Windows | .msi installer |
| `nsis` | Windows | .exe installer |

**Icons Configuration:**

```json
"icon": [
  "icons/32x32.png",
  "icons/64x64.png",
  "icons/128x128.png",
  "icons/128x128@2x.png",
  "icons/icon.png",
  "icons/icon.ico",    // Windows
  "icons/icon.icns"    // macOS
]
```

**Icon Requirements:**
- **Windows**: .ico with multiple sizes (16x16 to 256x256)
- **macOS**: .icns with retina support (@2x versions)
- **Linux**: PNG files at multiple resolutions
- **Recommended sizes**: 32, 64, 128, 256, 512, 1024 (all square)

**Resources and External Binaries:**

```json
"resources": ["config/*", "assets/*"],
"externalBin": ["binaries/claude"]
```

- **resources**: Extra files to include in bundle
- **externalBin**: External executables (must be in src-tauri/binaries/)
- **Access**: Resources via `$RESOURCE`, binaries via sidecar API

#### Linux-Specific Configuration

```json
"linux": {
  "appimage": {
    "bundleMediaFramework": true
  },
  "deb": {
    "depends": ["libwebkit2gtk-4.1-0", "libgtk-3-0"]
  }
}
```

**AppImage Options:**
- `bundleMediaFramework`: Include GStreamer for video/audio playback
- **When to Enable**: If app plays media files
- **Impact**: Increases bundle size by ~20-30MB

**Debian Package Dependencies:**
- `libwebkit2gtk-4.1-0`: WebView engine (REQUIRED)
- `libgtk-3-0`: GTK3 UI toolkit (REQUIRED)
- **Add dependencies**: System libraries your app needs
- **Example**: `["libssl3", "libpq5"]` for database apps

#### macOS-Specific Configuration

```json
"macOS": {
  "frameworks": [],
  "minimumSystemVersion": "10.15",
  "exceptionDomain": "",
  "signingIdentity": null,
  "providerShortName": null,
  "entitlements": "entitlements.plist",
  "dmg": {
    "windowSize": { "width": 540, "height": 380 },
    "appPosition": { "x": 140, "y": 200 },
    "applicationFolderPosition": { "x": 400, "y": 200 }
  }
}
```

**macOS Bundle Fields:**

| Field | Value | Purpose |
|-------|-------|---------|
| `frameworks` | `[]` | Additional frameworks to link |
| `minimumSystemVersion` | `"10.15"` | Minimum macOS version (Catalina) |
| `exceptionDomain` | `""` | Network security exceptions |
| `signingIdentity` | `null` | Code signing certificate (for App Store) |
| `providerShortName` | `null` | Team ID for notarization |
| `entitlements` | `"entitlements.plist"` | Permissions file |

**DMG Installer Layout:**
- `windowSize`: DMG finder window dimensions
- `appPosition`: Where app icon appears in DMG
- `applicationFolderPosition`: Where Applications folder link appears
- **Customize**: For branded installer appearance

**Code Signing (for Distribution):**

```json
"signingIdentity": "Apple Development: Your Name (TEAM_ID)",
"providerShortName": "TEAM_ID"
```

- Required for App Store and notarization
- Obtain from Apple Developer account
- Leave `null` for local development

---

## Rust/Cargo Configuration

### Location
`/Users/max/local/opcode/src-tauri/Cargo.toml`

### Package Metadata

```toml
[package]
name = "opcode"
version = "0.2.1"
description = "GUI app and Toolkit for Claude Code"
authors = ["mufeedvh", "123vviekr"]
license = "AGPL-3.0"
edition = "2021"
default-run = "opcode"
```

#### Field Reference

| Field | Value | Purpose | When to Change |
|-------|-------|---------|----------------|
| `name` | `"opcode"` | Crate name | Never after publish |
| `version` | `"0.2.1"` | Crate version | Before each release |
| `description` | String | Short description | When rebranding |
| `authors` | Array | Contributors | When adding authors |
| `license` | `"AGPL-3.0"` | License identifier | NEVER (legal implications) |
| `edition` | `"2021"` | Rust edition | When upgrading Rust |
| `default-run` | `"opcode"` | Default binary to run | If changing main binary |

**Critical: `default-run`**

```toml
default-run = "opcode"
```

- **Why Critical**: Project has multiple binaries (opcode, opcode-web)
- **Without This**: `cargo run` fails with "could not determine which binary to run"
- **Impact**: Tells Cargo to run "opcode" binary by default
- **Alternative**: `cargo run --bin opcode` (explicit)

### Binary Definitions

```toml
[[bin]]
name = "opcode"
path = "src/main.rs"

[[bin]]
name = "opcode-web"
path = "src/web_main.rs"
```

**Multiple Binaries:**
- `opcode`: Desktop GUI application (Tauri)
- `opcode-web`: Web server for mobile/browser access

**Running Specific Binaries:**
```bash
cargo run --bin opcode       # Desktop app
cargo run --bin opcode-web   # Web server
```

### Library Configuration

```toml
[lib]
name = "opcode_lib"
crate-type = ["lib", "cdylib", "staticlib"]
```

**Crate Types:**
- `lib`: Standard Rust library (for internal use)
- `cdylib`: C-compatible dynamic library (for FFI)
- `staticlib`: Static library (for embedding)

**When to Use:**
- **cdylib**: If exposing Rust functions to C/C++/Python
- **staticlib**: If embedding in other applications
- **lib only**: If only used internally (saves compile time)

### Build Dependencies

```toml
[build-dependencies]
tauri-build = { version = "2", features = [] }
```

- **Purpose**: Dependencies used in build.rs (build script)
- **tauri-build**: Generates Tauri boilerplate during compilation
- **When to Modify**: Only when Tauri releases new major version

### Runtime Dependencies

```toml
[dependencies]
# Tauri Core
tauri = { version = "2", features = [ "macos-private-api", "protocol-asset", "tray-icon", "image-png"] }
tauri-plugin-shell = "2"
tauri-plugin-dialog = "2"
tauri-plugin-fs = "2"
tauri-plugin-process = "2"
tauri-plugin-updater = "2"
tauri-plugin-notification = "2"
tauri-plugin-clipboard-manager = "2"
tauri-plugin-global-shortcut = "2"
tauri-plugin-http = "2"

# Serialization
serde = { version = "1", features = ["derive"] }
serde_json = "1"

# Async Runtime
tokio = { version = "1", features = ["full"] }

# Database
rusqlite = { version = "0.32", features = ["bundled"] }

# Utilities
dirs = "5"
chrono = { version = "0.4", features = ["serde"] }
anyhow = "1"
log = "0.4"
env_logger = "0.11"
regex = "1"
glob = "0.3"
base64 = "0.22"
libc = "0.2"

# HTTP Client
reqwest = { version = "0.12", features = ["json", "native-tls-vendored"] }

# Async Utilities
futures = "0.3"
async-trait = "0.1"

# File System
tempfile = "3"
walkdir = "2"

# Process Management
which = "7"

# Compression & Hashing
sha2 = "0.10"
zstd = "0.13"

# UUID Generation
uuid = { version = "1.6", features = ["v4", "serde"] }

# Web Server (for opcode-web)
axum = { version = "0.8", features = ["ws"] }
tower = "0.5"
tower-http = { version = "0.6", features = ["fs", "cors"] }

# CLI Parsing
clap = { version = "4.0", features = ["derive"] }

# Async Utilities
futures-util = "0.3"

# Image Processing
image = "=0.25.1"  # Pinned to avoid edition2024 requirement

# YAML Parsing
serde_yaml = "0.9"
```

#### Tauri Features Explained

| Feature | Purpose | When to Enable |
|---------|---------|----------------|
| `macos-private-api` | macOS transparency/vibrancy | For visual effects |
| `protocol-asset` | `asset://` protocol | To load local files |
| `tray-icon` | System tray support | For background apps |
| `image-png` | PNG image support | For icons/images |

#### Dependency Feature Flags

**tokio features:**
```toml
tokio = { version = "1", features = ["full"] }
```
- `"full"`: All tokio features (simple but bloated)
- **Better**: `["rt-multi-thread", "macros", "sync", "time", "fs", "io-util"]`
- **Impact**: "full" adds 20-30% to compile time

**rusqlite features:**
```toml
rusqlite = { version = "0.32", features = ["bundled"] }
```
- `"bundled"`: Bundles SQLite (no system dependency)
- **Alternative**: `[]` - uses system SQLite (smaller binary)
- **Recommendation**: Keep bundled for consistent behavior

**reqwest features:**
```toml
reqwest = { version = "0.12", features = ["json", "native-tls-vendored"] }
```
- `"json"`: Enable JSON serialization
- `"native-tls-vendored"`: Bundle OpenSSL (cross-platform)
- **Alternative**: `"rustls-tls"` - pure Rust TLS (smaller)

**Image Version Pinning:**
```toml
image = "=0.25.1"
```
- **Exact version**: Prevents automatic updates
- **Reason**: v0.26+ requires Rust 2024 edition
- **When to Unpin**: After upgrading to edition = "2024"

### Platform-Specific Dependencies

```toml
[target.'cfg(target_os = "macos")'.dependencies]
tauri = { version = "2", features = ["macos-private-api"] }
window-vibrancy = "0.5"
cocoa = "0.26"
objc = "0.2"
```

**macOS-Only Dependencies:**
- `window-vibrancy`: macOS window effects (blur, translucency)
- `cocoa`: macOS native API bindings
- `objc`: Objective-C runtime for macOS APIs

**Why Platform-Specific:**
- Reduces binary size on other platforms
- Avoids compilation errors on Linux/Windows
- Only compiles when `target_os = "macos"`

### Feature Flags

```toml
[features]
custom-protocol = ["tauri/custom-protocol"]
```

- **custom-protocol**: Required for production builds without dev server
- **When Enabled**: Automatically in release builds
- **Purpose**: Allows loading frontend via `tauri://` protocol
- **DO NOT REMOVE**: Required for production builds

### Release Profile Optimization

```toml
[profile.release]
strip = true
opt-level = "z"
lto = true
codegen-units = 1
```

#### Optimization Settings Explained

| Setting | Value | Purpose | Trade-off |
|---------|-------|---------|-----------|
| `strip` | `true` | Remove debug symbols | Smaller binary, no debugging |
| `opt-level` | `"z"` | Optimize for size | Smaller but slightly slower |
| `lto` | `true` | Link-time optimization | Smaller/faster but slow compile |
| `codegen-units` | `1` | Single codegen unit | Better optimization, slow compile |

**Optimization Levels:**
- `0`: No optimization (debug builds)
- `1`: Basic optimization
- `2`: Standard optimization (default release)
- `3`: Aggressive optimization (speed)
- `"s"`: Optimize for size
- `"z"`: Aggressively optimize for size

**Alternative Profiles:**

```toml
# Faster compilation, larger binary
[profile.release]
strip = true
opt-level = 2
lto = "thin"
codegen-units = 16

# Maximum performance (not size)
[profile.release-perf]
inherits = "release"
opt-level = 3
lto = "fat"
```

**Compile Time Comparison:**
- Debug build: ~20 seconds
- Release (current config): ~2-3 minutes
- Release (opt-level = 2): ~1-2 minutes

---

## Frontend Configuration

### Package.json

**Location:** `/Users/max/local/opcode/package.json`

```json
{
  "name": "opcode",
  "private": true,
  "version": "0.2.1",
  "license": "AGPL-3.0",
  "type": "module"
}
```

#### Root Fields

| Field | Value | Purpose |
|-------|-------|---------|
| `name` | `"opcode"` | Package name |
| `private` | `true` | Prevents accidental npm publish |
| `version` | `"0.2.1"` | Must match Cargo.toml and tauri.conf.json |
| `license` | `"AGPL-3.0"` | Open source license |
| `type` | `"module"` | Use ES modules (import/export) |

**Why `private: true`:**
- Prevents `npm publish` from working
- Not meant for npm registry
- Keeps internal dependencies private

#### Scripts

```json
"scripts": {
  "dev": "vite",
  "build": "tsc && vite build",
  "prebuild": "",
  "build:executables": "bun run scripts/fetch-and-build.js --version=1.0.41",
  "build:executables:current": "bun run scripts/fetch-and-build.js current --version=1.0.41",
  "build:executables:linux": "bun run scripts/fetch-and-build.js linux --version=1.0.41",
  "build:executables:macos": "bun run scripts/fetch-and-build.js macos --version=1.0.41",
  "build:executables:windows": "bun run scripts/fetch-and-build.js windows --version=1.0.41",
  "preview": "vite preview",
  "tauri": "tauri",
  "build:dmg": "tauri build --bundles dmg",
  "check": "tsc --noEmit && cd src-tauri && cargo check"
}
```

**Script Reference:**

| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `vite` | Start Vite dev server (NOT used in Tauri dev) |
| `build` | `tsc && vite build` | Type check + build frontend |
| `preview` | `vite preview` | Preview production build |
| `tauri` | `tauri` | Shortcut for Tauri CLI |
| `build:dmg` | `tauri build --bundles dmg` | Build macOS DMG only |
| `check` | `tsc --noEmit && cargo check` | Type check TS + Rust |
| `build:executables:*` | Custom script | Download/build Claude binaries |

**Important Note on `build` script:**
```json
"build": "tsc && vite build"
```
- **tsc**: Type checks TypeScript (fails on type errors)
- **vite build**: Compiles frontend to dist/
- **Why both**: Ensures type safety before building
- **Disable type check**: Remove `tsc &&` (faster but risky)

#### Dependencies

**UI Libraries:**
```json
"@radix-ui/react-dialog": "^1.1.4",
"@radix-ui/react-dropdown-menu": "^2.1.15",
"@radix-ui/react-tabs": "^1.1.3",
"@radix-ui/react-tooltip": "^1.1.5",
```
- Unstyled, accessible UI components
- Headless UI primitives for custom designs

**Styling:**
```json
"@tailwindcss/cli": "^4.1.8",
"@tailwindcss/vite": "^4.1.8",
"tailwindcss": "^4.1.8",
"tailwind-merge": "^2.6.0",
"class-variance-authority": "^0.7.1",
```
- Tailwind CSS v4 with Vite plugin
- `tailwind-merge`: Merge Tailwind classes intelligently
- `cva`: Component variants utility

**Tauri Integration:**
```json
"@tauri-apps/api": "^2.1.1",
"@tauri-apps/plugin-dialog": "^2.0.2",
"@tauri-apps/plugin-shell": "^2.0.1",
"@tauri-apps/plugin-global-shortcut": "^2.0.0",
```
- Must match Tauri version in Cargo.toml
- Provides TypeScript bindings for Rust commands

**State Management:**
```json
"zustand": "^5.0.6",
```
- Lightweight state management (simpler than Redux)

**Forms:**
```json
"react-hook-form": "^7.54.2",
"@hookform/resolvers": "^3.9.1",
"zod": "^3.24.1",
```
- `react-hook-form`: Form state management
- `zod`: TypeScript-first schema validation
- `@hookform/resolvers`: Bridges RHF + Zod

**Markdown & Code:**
```json
"react-markdown": "^9.0.3",
"remark-gfm": "^4.0.0",
"react-syntax-highlighter": "^15.6.1",
"@uiw/react-md-editor": "^4.0.7",
```
- Markdown rendering with GitHub Flavored Markdown
- Syntax highlighting for code blocks
- Markdown editor component

**Utilities:**
```json
"date-fns": "^3.6.0",
"diff": "^8.0.2",
"ansi-to-html": "^0.7.2",
```
- Date formatting and manipulation
- Text diff algorithms
- ANSI terminal output to HTML

**Analytics:**
```json
"posthog-js": "^1.258.3",
```
- Product analytics and feature flags
- Requires environment variables (see below)

#### Dev Dependencies

```json
"devDependencies": {
  "@tauri-apps/cli": "^2.7.1",
  "@types/node": "^22.15.30",
  "@types/react": "^18.3.1",
  "@types/react-dom": "^18.3.1",
  "@types/sharp": "^0.32.0",
  "@vitejs/plugin-react": "^4.3.4",
  "sharp": "^0.34.2",
  "typescript": "~5.6.2",
  "vite": "^6.0.3"
}
```

**TypeScript Types:**
- `@types/*`: Type definitions for libraries
- Required for TypeScript autocomplete

**Build Tools:**
- `vite`: Frontend build tool (fast!)
- `@vitejs/plugin-react`: React support for Vite
- `@tauri-apps/cli`: Tauri CLI tools

**Image Optimization:**
- `sharp`: Fast image processing (used in icon generation)

#### Trusted Dependencies

```json
"trustedDependencies": [
  "@parcel/watcher",
  "@tailwindcss/oxide"
]
```
- **Purpose**: Allows these packages to run install scripts
- **Security**: Only add trusted packages (scripts run with full access)
- **Why needed**: Native bindings require compilation

#### Optional Dependencies

```json
"optionalDependencies": {
  "@esbuild/linux-x64": "^0.25.6",
  "@rollup/rollup-linux-x64-gnu": "^4.45.1"
}
```
- **Purpose**: Platform-specific native dependencies
- **When missing**: Build continues (graceful degradation)
- **Use case**: Cross-platform development (e.g., building on macOS for Linux)

### Vite Configuration

**Location:** `/Users/max/local/opcode/vite.config.ts`

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath, URL } from "node:url";

const host = process.env.TAURI_DEV_HOST;

export default defineConfig(async () => ({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  clearScreen: false,
  server: { ... },
  build: { ... }
}));
```

#### Plugins

```typescript
plugins: [react(), tailwindcss()]
```

**react():**
- Enables React Fast Refresh (hot reload)
- JSX/TSX transformation
- React Developer Tools integration

**tailwindcss():**
- Tailwind CSS v4 Vite plugin
- Processes `@import "tailwindcss"`
- Lightning CSS for optimization

#### Path Alias

```typescript
resolve: {
  alias: {
    "@": fileURLToPath(new URL("./src", import.meta.url)),
  },
}
```

**Purpose:**
```typescript
// Instead of:
import { Button } from "../../../components/Button";

// Use:
import { Button } from "@/components/Button";
```

**Adding More Aliases:**
```typescript
alias: {
  "@": fileURLToPath(new URL("./src", import.meta.url)),
  "@components": fileURLToPath(new URL("./src/components", import.meta.url)),
  "@lib": fileURLToPath(new URL("./src/lib", import.meta.url)),
}
```

**Must Match:** `paths` in tsconfig.json

#### Server Configuration

```typescript
server: {
  port: 1420,
  strictPort: true,
  host: host || false,
  hmr: host
    ? {
        protocol: "ws",
        host,
        port: 1421,
      }
    : undefined,
  watch: {
    ignored: ["**/src-tauri/**"],
  },
}
```

**Port Settings:**

| Setting | Value | Purpose |
|---------|-------|---------|
| `port` | `1420` | Fixed port for Tauri (REQUIRED) |
| `strictPort` | `true` | Fail if port unavailable (don't auto-increment) |
| `host` | `false` | Localhost only (or from env var) |

**Why Port 1420:**
- Tauri expects this specific port in development
- Changing requires updating Tauri config
- Port conflicts will cause startup failure

**Hot Module Replacement (HMR):**
```typescript
hmr: {
  protocol: "ws",
  host,
  port: 1421,
}
```
- **Port 1421**: WebSocket for hot reload
- **Conditional**: Only when TAURI_DEV_HOST is set (for network access)
- **Local dev**: HMR uses default settings

**File Watching:**
```typescript
watch: {
  ignored: ["**/src-tauri/**"],
}
```
- Prevents Vite from watching Rust files
- Improves performance (fewer file system events)
- Rust changes trigger Cargo rebuild, not Vite

**Environment Variable: TAURI_DEV_HOST**
```bash
# Access dev server from other devices on network
export TAURI_DEV_HOST=192.168.1.100
bun run dev
```

#### Build Configuration

```typescript
build: {
  chunkSizeWarningLimit: 2000,
  rollupOptions: {
    output: {
      manualChunks: {
        'react-vendor': ['react', 'react-dom'],
        'ui-vendor': ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu', ...],
        'editor-vendor': ['@uiw/react-md-editor'],
        'syntax-vendor': ['react-syntax-highlighter'],
        'tauri': ['@tauri-apps/api', '@tauri-apps/plugin-dialog', ...],
        'utils': ['date-fns', 'clsx', 'tailwind-merge'],
      },
    },
  },
}
```

**Code Splitting Strategy:**

| Chunk | Packages | Purpose |
|-------|----------|---------|
| `react-vendor` | React core | Framework (rarely changes) |
| `ui-vendor` | Radix UI | UI components bundle |
| `editor-vendor` | MD editor | Lazy load if not on every page |
| `syntax-vendor` | Syntax highlighter | Lazy load for code display |
| `tauri` | Tauri APIs | Desktop integration |
| `utils` | Utilities | Small helpers |

**Why Code Splitting:**
- **Faster initial load**: Load only what's needed
- **Better caching**: Vendor chunks rarely change
- **Parallel downloads**: Browser loads chunks simultaneously
- **Smaller chunks**: Easier to debug and analyze

**Chunk Size Warning:**
```typescript
chunkSizeWarningLimit: 2000  // 2MB in KB
```
- Default is 500KB (too aggressive for rich apps)
- Increased to 2MB to avoid warnings
- Large chunks may impact initial load time

**Build Output:**
```
dist/
├── index.html
├── assets/
│   ├── index-abc123.js        # Main app code
│   ├── react-vendor-def456.js # React bundle
│   ├── ui-vendor-ghi789.js    # UI components
│   └── ...
```

---

## TypeScript Configuration

### Main TypeScript Config

**Location:** `/Users/max/local/opcode/tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    /* Path aliases */
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

#### Compiler Options Explained

**Target & Module:**

| Option | Value | Purpose |
|--------|-------|---------|
| `target` | `"ES2020"` | Output JavaScript version |
| `module` | `"ESNext"` | Use latest ES modules |
| `lib` | `["ES2020", "DOM", ...]` | Available APIs |

**Modern JavaScript Features (ES2020):**
- Optional chaining (`?.`)
- Nullish coalescing (`??`)
- BigInt support
- Dynamic import

**Bundler Mode:**
```json
"moduleResolution": "bundler",
"allowImportingTsExtensions": true,
```
- Optimized for Vite/bundlers
- Allows `.ts`/`.tsx` imports (bundler removes)
- Faster than "node" resolution

**Build Settings:**

| Option | Value | Reason |
|--------|-------|--------|
| `noEmit` | `true` | Vite handles compilation, TS only checks |
| `isolatedModules` | `true` | Each file is compiled independently (faster) |
| `skipLibCheck` | `true` | Don't type-check node_modules (faster) |

**React JSX:**
```json
"jsx": "react-jsx"
```
- Modern JSX transform (React 17+)
- No need to `import React` in every file
- Smaller bundle size

**Strict Type Checking:**

| Option | Effect |
|--------|--------|
| `strict` | Enable all strict checks |
| `noUnusedLocals` | Error on unused variables |
| `noUnusedParameters` | Error on unused function params |
| `noFallthroughCasesInSwitch` | Require break/return in switch |

**Disabling Strict Checks (not recommended):**
```json
"strict": false,
"noUnusedLocals": false,
// Faster compilation but less type safety
```

**Path Mapping:**
```json
"baseUrl": ".",
"paths": {
  "@/*": ["./src/*"]
}
```
- Must match Vite alias configuration
- Enables `import from "@/components/..."`

**Project References:**
```json
"references": [{ "path": "./tsconfig.node.json" }]
```
- Splits config for build scripts (vite.config.ts)
- Faster incremental builds

### Node TypeScript Config

**Location:** `/Users/max/local/opcode/tsconfig.node.json`

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

**Purpose:**
- Separate config for Node.js code (build scripts)
- Different from browser code in tsconfig.json

**Composite Projects:**
```json
"composite": true
```
- Enables project references
- Faster builds with incremental compilation
- Required for multi-project setups

---

## Build System Configuration

### Justfile

**Location:** `/Users/max/local/opcode/justfile`

The `justfile` is a command runner (alternative to Makefiles) that documents the intended build workflow.

#### Common Commands

```bash
just dev        # Build frontend + run desktop app
just web        # Build frontend + run web server
just quick      # Alias for dev
just build      # Full build (install deps + frontend + backend)
just clean      # Remove all build artifacts
just test       # Run Rust tests
just fmt        # Format Rust code
just check      # Type check TypeScript + Rust
```

#### Command Breakdown

**Development Workflow:**
```justfile
dev: build-frontend
    cd src-tauri && cargo run
```
- **Dependencies**: Runs `build-frontend` first
- **Purpose**: Standard dev workflow (build once, run)
- **Not Hot Reload**: Requires rebuild for frontend changes

**Web Server Mode:**
```justfile
web: build-frontend
    cd src-tauri && cargo run --bin opcode-web

web-port PORT: build-frontend
    cd src-tauri && cargo run --bin opcode-web -- --port {{PORT}}
```
- Runs web server binary for mobile/browser access
- Default port: 8080 (configurable)

**Build Commands:**
```justfile
build-frontend:
    npm run build

build-backend:
    cd src-tauri && cargo build

build-backend-release:
    cd src-tauri && cargo build --release
```

**Clean:**
```justfile
clean:
    rm -rf node_modules dist
    cd src-tauri && cargo clean
```
- Removes all build artifacts
- Use when switching branches or fixing build issues

**Network Access:**
```justfile
ip:
    @echo "🌐 Your PC's IP addresses:"
    @ip route get 1.1.1.1 | grep -oP 'src \K\S+' || echo "Could not detect IP"
    @echo "📱 Use this IP on your phone: http://YOUR_IP:8080"
```
- Shows local IP for mobile access
- Use with `just web` for remote testing

#### Customizing Justfile

**Adding New Commands:**
```justfile
# Format all code
format: fmt
    npm run format

# Type check everything
typecheck:
    npm run check
    cd src-tauri && cargo clippy

# Production build
release: build-frontend build-backend-release
    @echo "✅ Release build complete!"
    @ls -lh src-tauri/target/release/opcode
```

**Using Variables:**
```justfile
default_port := "8080"

web-default: build-frontend
    cd src-tauri && cargo run --bin opcode-web -- --port {{default_port}}
```

---

## macOS-Specific Configuration

### Entitlements (Permissions)

**Location:** `/Users/max/local/opcode/src-tauri/entitlements.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Sandbox disabled for Homebrew compatibility -->
    <key>com.apple.security.app-sandbox</key>
    <false/>

    <!-- Network access -->
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.network.server</key>
    <true/>

    <!-- File system access -->
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
    <key>com.apple.security.files.downloads.read-write</key>
    <true/>

    <!-- Subprocess spawning -->
    <key>com.apple.security.inherit</key>
    <true/>

    <!-- Automation -->
    <key>com.apple.security.automation.apple-events</key>
    <true/>

    <!-- Hardware -->
    <key>com.apple.security.device.camera</key>
    <true/>
    <key>com.apple.security.device.microphone</key>
    <true/>

    <!-- Printing -->
    <key>com.apple.security.print</key>
    <true/>

    <!-- Hardened Runtime (for code signing) -->
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.cs.disable-executable-page-protection</key>
    <true/>
</dict>
</plist>
```

#### Entitlements Reference

**Sandbox:**

| Key | Value | Purpose |
|-----|-------|---------|
| `com.apple.security.app-sandbox` | `false` | Disable App Sandbox |

**Why Disabled:**
- App spawns Claude CLI (requires full system access)
- Homebrew installs need unrestricted file access
- Sandbox restricts subprocess execution

**For App Store Distribution:**
```xml
<key>com.apple.security.app-sandbox</key>
<true/>
<key>com.apple.security.files.user-selected.read-write</key>
<true/>
```
- Enable sandbox and request specific permissions
- May require Apple review for subprocess execution

**Network Permissions:**

| Key | Purpose |
|-----|---------|
| `com.apple.security.network.client` | Make network requests |
| `com.apple.security.network.server` | Accept incoming connections |

**File Access:**

| Key | Purpose |
|-----|---------|
| `com.apple.security.files.user-selected.read-write` | Read/write user-selected files |
| `com.apple.security.files.downloads.read-write` | Access Downloads folder |

**Advanced: Specific Folder Access**
```xml
<key>com.apple.security.files.bookmarks.app-scope</key>
<true/>
<key>com.apple.security.files.bookmarks.document-scope</key>
<true/>
```

**Process Execution:**

| Key | Purpose |
|-----|---------|
| `com.apple.security.inherit` | Spawn subprocesses |

**Required for:** Running Claude CLI, git, npm, etc.

**Hardware Access:**

| Key | Purpose |
|-----|---------|
| `com.apple.security.device.camera` | Camera access |
| `com.apple.security.device.microphone` | Microphone access |

**When to Remove:**
- If app doesn't use camera/mic
- Reduces privacy concerns in macOS prompts

**Hardened Runtime (Code Signing):**

| Key | Purpose |
|-----|---------|
| `cs.allow-unsigned-executable-memory` | Allow JIT compilation |
| `cs.allow-jit` | Just-in-time compilation |
| `cs.disable-library-validation` | Load unsigned libraries |
| `cs.disable-executable-page-protection` | Allow dynamic code |

**Security Trade-offs:**
- Required for some features (WebAssembly, plugins)
- Reduces security hardening
- May prevent App Store approval

**Minimal Hardened Runtime:**
```xml
<!-- Only allow JIT for specific use cases -->
<key>com.apple.security.cs.allow-jit</key>
<true/>
<!-- Remove other cs.* keys -->
```

### Info.plist (Bundle Metadata)

**Location:** `/Users/max/local/opcode/src-tauri/Info.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>NSRequiresAquaSystemAppearance</key>
  <false/>
  <key>LSMinimumSystemVersion</key>
  <string>10.15</string>
  <key>CFBundleShortVersionString</key>
  <string>0.2.1</string>
  <key>CFBundleName</key>
  <string>opcode</string>
  <key>CFBundleDisplayName</key>
  <string>opcode</string>
  <key>CFBundleIdentifier</key>
  <string>opcode.asterisk.so</string>
  <key>CFBundleDocumentTypes</key>
  <array>...</array>
  <key>NSAppleEventsUsageDescription</key>
  <string>opcode needs to send Apple Events to other applications.</string>
  <key>NSCameraUsageDescription</key>
  <string>opcode needs camera access for capturing images for AI processing.</string>
  <key>NSMicrophoneUsageDescription</key>
  <string>opcode needs microphone access for voice input features.</string>
</dict>
</plist>
```

#### Info.plist Fields

**App Metadata:**

| Key | Value | Purpose |
|-----|-------|---------|
| `CFBundleName` | `"opcode"` | Internal app name |
| `CFBundleDisplayName` | `"opcode"` | Name shown in UI |
| `CFBundleIdentifier` | `"opcode.asterisk.so"` | Unique bundle ID |
| `CFBundleShortVersionString` | `"0.2.1"` | User-visible version |

**System Requirements:**

| Key | Value | Purpose |
|-----|-------|---------|
| `LSMinimumSystemVersion` | `"10.15"` | macOS Catalina minimum |

**Supported Versions:**
- `10.15`: macOS Catalina (2019)
- `11.0`: macOS Big Sur (2020)
- `12.0`: macOS Monterey (2021)
- `13.0`: macOS Ventura (2022)

**Dark Mode Support:**

```xml
<key>NSRequiresAquaSystemAppearance</key>
<false/>
```
- `false`: App supports dark mode
- `true`: Force light mode (legacy apps)

**Privacy Descriptions:**

macOS requires user-facing explanations for permission requests:

| Key | Description |
|-----|-------------|
| `NSCameraUsageDescription` | Why app needs camera |
| `NSMicrophoneUsageDescription` | Why app needs microphone |
| `NSAppleEventsUsageDescription` | Why app sends events |

**Adding More Privacy Keys:**
```xml
<key>NSPhotoLibraryUsageDescription</key>
<string>opcode needs to save screenshots to your Photos library.</string>

<key>NSLocationWhenInUseUsageDescription</key>
<string>opcode uses your location for [specific feature].</string>
```

**Document Types (File Associations):**

```xml
<key>CFBundleDocumentTypes</key>
<array>
  <dict>
    <key>CFBundleTypeName</key>
    <string>opcode Agent</string>
    <key>CFBundleTypeRole</key>
    <string>Editor</string>
    <key>CFBundleTypeExtensions</key>
    <array>
      <string>opcode.json</string>
    </array>
    <key>CFBundleTypeIconFile</key>
    <string>icon.icns</string>
    <key>LSHandlerRank</key>
    <string>Owner</string>
  </dict>
</array>
```

**File Association Fields:**

| Key | Value | Purpose |
|-----|-------|---------|
| `CFBundleTypeName` | User-visible type name | Shows in "Kind" column |
| `CFBundleTypeRole` | `"Editor"` or `"Viewer"` | How app handles files |
| `CFBundleTypeExtensions` | Array of extensions | `.opcode.json` in this case |
| `LSHandlerRank` | `"Owner"` | Priority (Owner > Default > Alternate) |

**URL Schemes (Deep Links):**
```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLName</key>
    <string>opcode URL</string>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>opcode</string>
    </array>
  </dict>
</array>
```
- Enables `opcode://` URLs
- Open app from browser/terminal

---

## Security & Permissions

### Tauri Capabilities

**Location:** `/Users/max/local/opcode/src-tauri/capabilities/default.json`

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Capability for the main window",
  "windows": ["main"],
  "permissions": [...]
}
```

#### Permission System

Tauri 2 uses a declarative permission system where each API requires explicit permission.

**Core Permissions:**
```json
"core:default",
"dialog:default",
"shell:allow-execute",
"shell:allow-spawn",
"shell:allow-open",
"fs:default",
"http:default",
"process:default",
"notification:default",
"clipboard-manager:default",
"global-shortcut:default",
"updater:default"
```

**Permission Types:**

| Type | Scope | Example |
|------|-------|---------|
| `*:default` | Plugin defaults | `dialog:default` |
| `*:allow-*` | Specific action | `fs:allow-read` |
| `*:deny-*` | Block action | `fs:deny-write` |
| Object | Fine-grained | Shell command allowlist |

#### Shell Permissions (Command Execution)

```json
{
  "identifier": "shell:allow-execute",
  "allow": [
    {
      "name": "claude",
      "sidecar": false,
      "args": true
    }
  ]
}
```

**Shell Permission Fields:**

| Field | Value | Purpose |
|-------|-------|---------|
| `name` | `"claude"` | Command name (must be in PATH) |
| `sidecar` | `false` | Not a bundled binary |
| `args` | `true` | Allow passing arguments |

**Security Best Practices:**

1. **Allowlist specific commands:**
```json
"allow": [
  { "name": "claude", "args": true },
  { "name": "git", "args": ["status", "diff", "log"] },
  { "name": "node", "args": false }
]
```

2. **Use sidecars for bundled binaries:**
```json
{
  "name": "my-binary",
  "sidecar": true,
  "args": true
}
```

3. **Deny dangerous commands:**
```json
"deny": ["rm", "del", "format", "sudo"]
```

#### Filesystem Permissions

```json
"fs:default",
"fs:allow-mkdir",
"fs:allow-read",
"fs:allow-write",
"fs:allow-remove",
"fs:allow-rename",
"fs:allow-exists",
"fs:allow-copy-file",
"fs:read-all",
"fs:write-all",
"fs:scope-app-recursive",
"fs:scope-home-recursive"
```

**Scope-based Permissions:**

| Scope | Access |
|-------|--------|
| `fs:scope-home-recursive` | Full access to home directory |
| `fs:scope-app-recursive` | Access to app directory |
| `fs:read-all` | Read any file in scope |
| `fs:write-all` | Write any file in scope |

**Restricting File Access:**
```json
"fs:scope": {
  "allow": [
    "$HOME/.claude/**",
    "$HOME/Documents/**"
  ],
  "deny": [
    "$HOME/.ssh/**",
    "$HOME/.aws/**"
  ]
}
```

#### Window Permissions

```json
"core:window:allow-minimize",
"core:window:allow-maximize",
"core:window:allow-unmaximize",
"core:window:allow-close",
"core:window:allow-is-maximized",
"core:window:allow-start-dragging"
```

**Why Explicit Window Permissions:**
- Custom title bar implementations
- Window controls from React components
- Each button requires specific permission

**All Available Window Permissions:**
```json
"core:window:allow-minimize",
"core:window:allow-maximize",
"core:window:allow-unmaximize",
"core:window:allow-close",
"core:window:allow-show",
"core:window:allow-hide",
"core:window:allow-set-decorations",
"core:window:allow-set-size",
"core:window:allow-set-position",
"core:window:allow-set-fullscreen",
"core:window:allow-set-focus",
"core:window:allow-set-title",
"core:window:allow-start-dragging",
"core:window:allow-start-resize-dragging"
```

#### HTTP Permissions

```json
"http:default",
"http:allow-fetch"
```

**Restricting HTTP Access:**
```json
{
  "identifier": "http:allow-fetch",
  "allow": [
    {
      "url": "https://api.anthropic.com/*"
    },
    {
      "url": "https://*.posthog.com/*"
    }
  ]
}
```

### Content Security Policy

See [Tauri Configuration > Security > CSP](#security-configuration) for detailed CSP documentation.

---

## Git Configuration

### Root .gitignore

**Location:** `/Users/max/local/opcode/.gitignore`

```gitignore
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

# Dependencies
node_modules

# Build outputs
dist
dist-ssr
*.local
*.bun-build

# Tauri binaries
src-tauri/binaries/

# Editor
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj*
*.sln
*.sw?
temp_lib/

# Environment
.env
```

#### Patterns Explained

**Build Artifacts:**
- `dist/`: Vite build output (regenerated)
- `dist-ssr/`: Server-side rendering build
- `*.bun-build`: Bun compilation cache

**Binaries:**
- `src-tauri/binaries/`: External executables (Claude CLI, etc.)
- Not committed (downloaded via scripts)

**Editor Files:**
- `.vscode/*`: VS Code settings
- `!.vscode/extensions.json`: Except recommended extensions
- `.idea/`: JetBrains IDEs
- `.DS_Store`: macOS folder metadata

**Why Keep .vscode/extensions.json:**
```json
{
  "recommendations": [
    "tauri-apps.tauri-vscode",
    "rust-lang.rust-analyzer",
    "bradlc.vscode-tailwindcss"
  ]
}
```
- Recommends extensions to contributors
- Improves onboarding experience

### Tauri .gitignore

**Location:** `/Users/max/local/opcode/src-tauri/.gitignore`

```gitignore
# Cargo build outputs
/target/

# Tauri generated schemas
/gen/schemas
```

**Target Directory:**
- All Rust compilation artifacts
- Can be GBs in size
- Regenerated by `cargo build`

**Generated Schemas:**
- Auto-generated from Tauri config
- Used for IDE autocomplete in capabilities
- Regenerated on build

---

## Environment Variables

### Frontend Environment Variables

**Usage in Code:**
```typescript
// src/main.tsx
import.meta.env.VITE_PUBLIC_POSTHOG_KEY
import.meta.env.VITE_PUBLIC_POSTHOG_HOST
```

**Expected Variables:**

| Variable | Purpose | Required |
|----------|---------|----------|
| `VITE_PUBLIC_POSTHOG_KEY` | PostHog API key | No (analytics disabled if missing) |
| `VITE_PUBLIC_POSTHOG_HOST` | PostHog server URL | No |

**Configuration Methods:**

1. **.env file** (not committed):
```bash
# .env
VITE_PUBLIC_POSTHOG_KEY=phc_xxxxx
VITE_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

2. **Environment variables:**
```bash
export VITE_PUBLIC_POSTHOG_KEY=phc_xxxxx
bun run build
```

3. **Command line:**
```bash
VITE_PUBLIC_POSTHOG_KEY=phc_xxxxx bun run build
```

**Vite Environment Variable Rules:**

- Must start with `VITE_` to be exposed to frontend
- `VITE_PUBLIC_*`: Safe for public exposure
- Available via `import.meta.env.*`
- Not available in Node.js code (only browser)

**Adding New Environment Variables:**

```typescript
// vite-env.d.ts
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_PUBLIC_POSTHOG_KEY: string;
  // Add more as needed
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

```bash
# .env
VITE_API_URL=https://api.example.com
```

### Backend Environment Variables

**Rust Environment Variables:**

| Variable | Purpose | When Set |
|----------|---------|----------|
| `RUST_LOG` | Logging level | Development |
| `RUST_BACKTRACE` | Stack traces on panic | Debugging |

**Usage:**
```bash
export RUST_LOG=debug
export RUST_BACKTRACE=1
cargo run
```

**Log Levels:**
- `error`: Only errors
- `warn`: Warnings and errors
- `info`: Info, warnings, errors
- `debug`: Debug + above
- `trace`: Everything

**Tauri Environment Variables:**

| Variable | Purpose |
|----------|---------|
| `TAURI_DEV_HOST` | Dev server host for network access |
| `TAURI_PLATFORM` | Override platform detection |
| `TAURI_DEBUG` | Enable debug features |

---

## Configuration Interdependencies

### Version Synchronization

**Critical:** These must match across all files:

```toml
# src-tauri/Cargo.toml
version = "0.2.1"
```

```json
// package.json
"version": "0.2.1"
```

```json
// src-tauri/tauri.conf.json
"version": "0.2.1"
```

```xml
<!-- src-tauri/Info.plist -->
<key>CFBundleShortVersionString</key>
<string>0.2.1</string>
```

**Update Checklist:**
1. Decide new version (semantic versioning)
2. Update Cargo.toml
3. Update package.json
4. Update tauri.conf.json
5. Info.plist updates automatically from tauri.conf.json

### Bundle Identifier Synchronization

```json
// tauri.conf.json
"identifier": "opcode.asterisk.so"
```

```xml
<!-- Info.plist -->
<key>CFBundleIdentifier</key>
<string>opcode.asterisk.so</string>
```

**Never change after first release!**

### Path Alias Synchronization

```typescript
// vite.config.ts
resolve: {
  alias: {
    "@": fileURLToPath(new URL("./src", import.meta.url)),
  },
}
```

```json
// tsconfig.json
"paths": {
  "@/*": ["./src/*"]
}
```

**Must match or TypeScript/Vite will be out of sync!**

### Port Configuration

```typescript
// vite.config.ts
server: {
  port: 1420,
  hmr: { port: 1421 }
}
```

**Tauri expects port 1420 in development mode.**

If changing, must also update:
- Any documentation
- Team knowledge base
- CI/CD scripts

### Frontend Dist Path

```json
// tauri.conf.json
"build": {
  "frontendDist": "../dist"
}
```

```typescript
// vite.config.ts (default, not specified)
build: {
  outDir: "dist"  // default value
}
```

**If changing Vite outDir:**
1. Update vite.config.ts: `outDir: "build"`
2. Update tauri.conf.json: `"frontendDist": "../build"`

### Filesystem Scope Synchronization

```json
// tauri.conf.json
"plugins": {
  "fs": {
    "scope": ["$HOME/**"]
  }
}
```

```json
// capabilities/default.json
"fs:scope-home-recursive"
```

**Both must allow the same paths!**

---

## Troubleshooting Misconfigurations

### Version Mismatch Issues

**Symptom:** Build fails or app shows wrong version

**Check:**
```bash
grep -r "0.2.1" package.json src-tauri/Cargo.toml src-tauri/tauri.conf.json
```

**Fix:** Update all to match

### Port Already in Use

**Symptom:**
```
Port 1420 is already in use
```

**Solutions:**
1. Kill process using port: `lsof -ti:1420 | xargs kill`
2. Change port in vite.config.ts (not recommended)
3. Set `strictPort: false` (auto-increments, breaks Tauri)

### Frontend Not Found

**Symptom:**
```
The `frontendDist` configuration is set to "../dist" but this path doesn't exist
```

**Cause:** Forgot to run `bun run build`

**Fix:**
```bash
bun run build
bun run tauri dev
```

### Multiple Binaries Error

**Symptom:**
```
error: `cargo run` could not determine which binary to run
```

**Fix:** Ensure `default-run = "opcode"` in Cargo.toml

### TypeScript Path Alias Not Working

**Symptom:** `import from "@/components"` shows error

**Check:**
1. vite.config.ts has matching alias
2. tsconfig.json has matching paths
3. Restart TypeScript server in IDE

### Permission Denied (macOS)

**Symptom:** App crashes with permission errors

**Check:**
1. entitlements.plist has required permissions
2. Rebuild app after changing entitlements
3. Check System Preferences > Security & Privacy

### CSP Blocking Resources

**Symptom:** Images/scripts not loading, console errors

**Check:** Browser DevTools console for CSP violations

**Fix:** Add domain to appropriate CSP directive in tauri.conf.json

### Tauri Plugin Version Mismatch

**Symptom:** Compilation errors about missing types

**Cause:** Rust plugin version != JS plugin version

**Fix:**
```bash
# Check versions
grep tauri-plugin package.json
grep tauri-plugin src-tauri/Cargo.toml

# Update both to match (e.g., all to version 2.0.0)
```

---

## Configuration Best Practices

### 1. Version Control

**Always commit:**
- All configuration files
- .gitignore patterns
- Schema files (if manually created)

**Never commit:**
- .env files (contains secrets)
- Build outputs (dist/, target/)
- node_modules/
- Platform-specific binaries

### 2. Development vs Production

**Separate configs for environments:**

```typescript
// vite.config.ts
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  build: {
    sourcemap: mode === 'development',
    minify: mode === 'production',
  }
}));
```

**Tauri build modes:**
- `tauri dev`: Development (debug Rust, unminified frontend)
- `tauri build`: Production (optimized Rust, minified frontend)

### 3. Security Hardening

**Before Production:**

1. **Minimize CSP directives:**
   - Remove `'unsafe-eval'` if possible
   - Limit `'unsafe-inline'` to specific resources
   - Allowlist only required domains

2. **Restrict filesystem scope:**
   ```json
   "scope": [
     "$HOME/.claude/**"  // Only app-specific directory
   ]
   ```

3. **Limit shell commands:**
   ```json
   "allow": [
     { "name": "claude", "args": true }
     // Remove development-only commands
   ]
   ```

4. **Review entitlements:**
   - Remove camera/mic if not used
   - Enable sandbox if possible
   - Minimize hardened runtime exceptions

### 4. Performance Tuning

**Frontend:**
- Enable code splitting (already configured)
- Use lazy loading for routes
- Optimize chunk sizes
- Enable compression

**Backend:**
- Use `opt-level = "z"` for size
- Use `opt-level = 3` for speed
- Profile with `cargo flamegraph`

### 5. Documentation

**Update when changing configs:**
- This configuration reference
- README.md
- CLAUDE.md (project notes)
- Comments in config files

---

## Common Configuration Patterns

### Adding a New Tauri Plugin

**1. Install Rust crate:**
```toml
# Cargo.toml
[dependencies]
tauri-plugin-store = "2"
```

**2. Install JS package:**
```bash
bun add @tauri-apps/plugin-store
```

**3. Add permissions:**
```json
// capabilities/default.json
"permissions": [
  "store:default",
  "store:allow-get",
  "store:allow-set"
]
```

**4. Initialize in Rust:**
```rust
// main.rs
fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_store::Builder::default().build())
        .run(tauri::generate_context!())
        .expect("error while running application");
}
```

### Adding a New Frontend Library

**1. Install package:**
```bash
bun add library-name
bun add -D @types/library-name
```

**2. Update code splitting (if large):**
```typescript
// vite.config.ts
manualChunks: {
  'library-name': ['library-name']
}
```

**3. Update CSP if needed:**
```json
// tauri.conf.json
"csp": "... ; script-src 'self' https://cdn.library.com"
```

### Adding Environment-Specific Configs

**1. Create .env files:**
```bash
.env                 # Default
.env.development     # Dev overrides
.env.production      # Prod overrides
```

**2. Use in Vite:**
```typescript
// vite.config.ts
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');

  return {
    define: {
      __API_URL__: JSON.stringify(env.VITE_API_URL)
    }
  };
});
```

### Cross-Platform Configuration

**Platform-specific dependencies:**
```toml
[target.'cfg(target_os = "macos")'.dependencies]
window-vibrancy = "0.5"

[target.'cfg(target_os = "windows")'.dependencies]
windows = "0.48"

[target.'cfg(target_os = "linux")'.dependencies]
webkit2gtk = "0.18"
```

**Platform detection in config:**
```typescript
// vite.config.ts
const isMacOS = process.platform === 'darwin';

export default defineConfig({
  build: {
    target: isMacOS ? 'safari13' : 'chrome90'
  }
});
```

---

## Configuration Validation

### Automated Checks

**Add to package.json:**
```json
"scripts": {
  "validate": "bun run validate:ts && bun run validate:rust",
  "validate:ts": "tsc --noEmit",
  "validate:rust": "cd src-tauri && cargo check"
}
```

**Pre-commit hook:**
```bash
# .husky/pre-commit
#!/bin/sh
bun run validate
```

### Manual Validation Checklist

Before committing config changes:

- [ ] Versions match across all files
- [ ] Bundle identifier unchanged (or intentionally changed)
- [ ] Path aliases match in TS and Vite configs
- [ ] Ports not conflicting
- [ ] CSP allows all required resources
- [ ] Filesystem scope allows necessary paths
- [ ] All required permissions granted
- [ ] Dev and production modes tested
- [ ] Documentation updated

---

## Summary

This configuration reference documents all configuration files in the Opcode project:

**Core Configurations:**
1. **Tauri** (tauri.conf.json) - App metadata, build, security, plugins, bundling
2. **Rust** (Cargo.toml) - Dependencies, binaries, features, optimization
3. **Frontend** (package.json, vite.config.ts) - Dependencies, scripts, build setup
4. **TypeScript** (tsconfig.json) - Type checking, modules, paths
5. **Build System** (justfile) - Command workflows

**Platform-Specific:**
6. **macOS** (entitlements.plist, Info.plist) - Permissions, metadata
7. **Security** (capabilities/default.json) - Fine-grained permissions

**Version Control:**
8. **Git** (.gitignore) - Excluded files/directories

**Runtime:**
9. **Environment Variables** - API keys, feature flags

**Key Takeaways:**
- Versions must be synchronized across 4 files
- `default-run` is critical for multi-binary projects
- CSP and permissions must be carefully configured
- Path aliases must match in Vite and TypeScript
- macOS requires extensive entitlements
- Code splitting improves load performance
- Validation prevents common misconfigurations

For questions or issues, refer to specific sections above or consult the Tauri documentation.
