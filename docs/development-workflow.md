# Development Workflow Guide

**A comprehensive guide for developers working on opcode.**

This document covers the complete development lifecycle, from initial setup through release deployment. Whether you're a new contributor or a seasoned developer, this guide will help you navigate the opcode codebase effectively.

---

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [IDE Configuration](#ide-configuration)
- [Code Organization](#code-organization)
- [Development Workflows](#development-workflows)
- [Adding New Features](#adding-new-features)
- [Testing Guidelines](#testing-guidelines)
- [Debugging Techniques](#debugging-techniques)
- [Hot Reload Behavior](#hot-reload-behavior)
- [Performance Optimization](#performance-optimization)
- [Code Style Guidelines](#code-style-guidelines)
- [Git Workflow](#git-workflow)
- [Pull Request Process](#pull-request-process)
- [Common Pitfalls](#common-pitfalls)
- [Release Process](#release-process)

---

## Development Environment Setup

### Prerequisites

Ensure you have the following tools installed:

#### Required Tools

1. **Bun** (latest version, currently 1.3.0+)
   ```bash
   curl -fsSL https://bun.sh/install | bash
   # Adds to ~/.bun/bin/bun
   ```

2. **Rust** (1.70.0+, currently 1.90.0+)
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
   # Adds to ~/.cargo/bin/
   ```

3. **Claude Code CLI**
   - Download from [Claude's official site](https://claude.ai/code)
   - Ensure `claude` is available in your PATH
   - Verify: `claude --version`

4. **Git**
   ```bash
   # macOS: brew install git
   # Linux: sudo apt install git
   # Windows: Download from https://git-scm.com
   ```

#### Platform-Specific Dependencies

**Linux (Ubuntu/Debian)**
```bash
sudo apt update && sudo apt install -y \
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

**macOS**
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Optional: Install pkg-config via Homebrew
brew install pkg-config
```

**Windows**
- Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Install [WebView2](https://developer.microsoft.com/microsoft-edge/webview2/) (pre-installed on Windows 11)

### Initial Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/getAsterisk/opcode.git
   cd opcode
   ```

2. **Install Frontend Dependencies**
   ```bash
   bun install
   ```

3. **Verify Installation**
   ```bash
   # Check tool versions
   cargo --version  # Should be 1.90.0+
   rustc --version  # Should be 1.90.0+
   bun --version    # Should be 1.3.0+
   claude --version # Should show Claude Code CLI version
   ```

4. **Add Cargo to PATH (if needed)**

   If you see "cargo not found" errors:
   ```bash
   # Add to ~/.zshrc or ~/.bashrc
   source "$HOME/.cargo/env"

   # Then reload shell
   exec $SHELL
   ```

### Environment Variables

The project uses the following environment variables:

- `TAURI_DEV_HOST`: Optional, for custom dev host configuration
- `RUST_LOG`: Controls logging verbosity (e.g., `debug`, `info`, `error`)
- `PATH`: Must include `~/.cargo/bin`, `~/.bun/bin`, and Claude Code CLI

---

## IDE Configuration

### Recommended IDEs

- **VS Code** (Recommended)
- **Cursor** (AI-powered fork of VS Code)
- **WebStorm** (for frontend)
- **RustRover** / **IntelliJ IDEA with Rust plugin** (for backend)

### VS Code Extensions

Install these extensions for the best development experience:

#### Frontend Development
- **ESLint** (`dbaeumer.vscode-eslint`)
- **Prettier** (`esbenp.prettier-vscode`)
- **TypeScript** (built-in)
- **Tailwind CSS IntelliSense** (`bradlc.vscode-tailwindcss`)
- **ES7+ React/Redux/React-Native snippets** (`dsznajder.es7-react-js-snippets`)

#### Backend Development
- **rust-analyzer** (`rust-lang.rust-analyzer`)
- **crates** (`serayuzgur.crates`) - Manage Cargo dependencies
- **Better TOML** (`bungcip.better-toml`)

#### Tauri Development
- **Tauri** (`tauri-apps.tauri-vscode`)

#### General
- **Error Lens** (`usernamehw.errorlens`) - Inline error highlighting
- **GitLens** (`eamodio.gitlens`) - Enhanced Git capabilities
- **Path Intellisense** (`christian-kohler.path-intellisense`)

### VS Code Settings

Create `.vscode/settings.json` in the project root:

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[rust]": {
    "editor.defaultFormatter": "rust-lang.rust-analyzer",
    "editor.formatOnSave": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "rust-analyzer.checkOnSave.command": "clippy",
  "rust-analyzer.cargo.features": "all",
  "tailwindCSS.experimental.classRegex": [
    ["cn\\(([^)]*)\\)", "(?:'|\"|`)([^'\"`]*)(?:'|\"|`)"]
  ]
}
```

### Recommended Terminal Setup

For the best terminal experience:

```bash
# Use iTerm2 on macOS or Windows Terminal on Windows
# Configure shell profile to auto-load Cargo environment

# Add to ~/.zshrc or ~/.bashrc:
source "$HOME/.cargo/env"
export PATH="$HOME/.bun/bin:$PATH"

# Optional: Add aliases for common commands
alias op-dev="bun run tauri dev"
alias op-build="bun run build"
alias op-test="cd src-tauri && cargo test"
alias op-fmt="cd src-tauri && cargo fmt"
alias op-check="bun run check"
```

---

## Code Organization

### Project Structure

```
opcode/
├── src/                          # React frontend (TypeScript)
│   ├── components/               # React components
│   │   ├── ui/                   # Reusable UI components (shadcn/ui)
│   │   ├── widgets/              # Tool-specific widgets (Bash, Todo, LS)
│   │   └── claude-code-session/  # Session management components
│   ├── lib/                      # Utility libraries
│   │   ├── analytics/            # PostHog analytics integration
│   │   ├── api.ts                # Type definitions and API interfaces
│   │   ├── apiAdapter.ts         # Tauri/Web API adapter
│   │   ├── hooksManager.ts       # Git hooks management
│   │   └── utils.ts              # General utilities
│   ├── contexts/                 # React contexts
│   │   ├── TabContext.tsx        # Tab management state
│   │   └── ThemeContext.tsx      # Theme switching
│   ├── hooks/                    # Custom React hooks
│   ├── assets/                   # Static assets (images, icons)
│   └── main.tsx                  # React entry point
│
├── src-tauri/                    # Rust backend (Tauri)
│   ├── src/
│   │   ├── commands/             # Tauri command handlers
│   │   │   ├── agents.rs         # Agent CRUD and execution
│   │   │   ├── claude.rs         # Claude Code CLI integration
│   │   │   ├── mcp.rs            # MCP server management
│   │   │   ├── proxy.rs          # HTTP proxy configuration
│   │   │   ├── slash_commands.rs # Slash command management
│   │   │   ├── storage.rs        # Database operations
│   │   │   ├── usage.rs          # Usage tracking and analytics
│   │   │   └── mod.rs            # Module exports
│   │   ├── checkpoint/           # Session checkpoint system
│   │   │   ├── manager.rs        # Checkpoint creation/restoration
│   │   │   ├── state.rs          # Checkpoint state management
│   │   │   ├── storage.rs        # Checkpoint file storage
│   │   │   └── mod.rs            # Module exports
│   │   ├── process/              # Process management
│   │   │   ├── registry.rs       # Process tracking registry
│   │   │   └── mod.rs            # Module exports
│   │   ├── claude_binary.rs      # Claude CLI binary detection
│   │   ├── web_server.rs         # Web server mode (opcode-web)
│   │   ├── main.rs               # Desktop app entry (opcode binary)
│   │   ├── web_main.rs           # Web server entry (opcode-web binary)
│   │   └── lib.rs                # Library exports
│   ├── Cargo.toml                # Rust dependencies and config
│   ├── tauri.conf.json           # Tauri application config
│   └── build.rs                  # Build script
│
├── public/                       # Public static assets
├── dist/                         # Built frontend (generated by Vite)
├── docs/                         # Documentation
├── .github/workflows/            # CI/CD workflows
│   ├── pr-check.yml              # PR validation
│   ├── release.yml               # Release automation
│   ├── build-linux.yml           # Linux build
│   └── build-macos.yml           # macOS build
├── package.json                  # Frontend dependencies and scripts
├── vite.config.ts                # Vite configuration
├── tsconfig.json                 # TypeScript configuration
├── justfile                      # Just commands (alternative build tool)
├── CLAUDE.md                     # Project-specific Claude Code instructions
└── README.md                     # Project overview
```

### Code Organization Principles

#### Frontend (React/TypeScript)

1. **Component Organization**
   - **UI Components** (`src/components/ui/`): Reusable, generic UI elements (buttons, dialogs, inputs)
   - **Feature Components** (`src/components/`): Business logic components (ClaudeCodeSession, Agents, Settings)
   - **Widgets** (`src/components/widgets/`): Specialized tool widgets (BashWidget, TodoWidget, LSWidget)
   - **Subcomponents** (`src/components/{feature}/`): Component-specific subcomponents (e.g., `claude-code-session/MessageList.tsx`)

2. **File Naming Conventions**
   - **Components**: PascalCase (e.g., `ClaudeCodeSession.tsx`)
   - **Utilities**: camelCase (e.g., `apiAdapter.ts`)
   - **Types**: PascalCase interfaces/types (e.g., `Project`, `Session`)
   - **Hooks**: camelCase with `use` prefix (e.g., `useTrackEvent`)

3. **State Management**
   - **Local State**: Use `useState` for component-specific state
   - **Context**: Use React Context for shared state (tabs, theme)
   - **Zustand**: For complex global state management
   - **API State**: Managed via `apiAdapter.ts` with React Query patterns

4. **Import Order**
   - React imports first
   - Third-party libraries
   - Internal components/utilities
   - Types/interfaces
   - Styles (if any)

   ```typescript
   import React, { useState, useEffect } from "react";
   import { motion } from "framer-motion";
   import { Button } from "@/components/ui/button";
   import { api, type Session } from "@/lib/api";
   import type { ClaudeStreamMessage } from "./AgentExecution";
   ```

#### Backend (Rust)

1. **Module Organization**
   - **Commands** (`src/commands/`): Tauri command handlers organized by feature
   - **Domain Logic** (`src/checkpoint/`, `src/process/`): Business logic modules
   - **Utilities** (`src/claude_binary.rs`): Shared utilities

2. **File Naming Conventions**
   - **Modules**: snake_case (e.g., `claude_binary.rs`)
   - **Types**: PascalCase (e.g., `ClaudeProcessState`)
   - **Functions**: snake_case (e.g., `execute_claude_code`)

3. **Command Pattern**
   - All Tauri commands are async functions marked with `#[tauri::command]`
   - Commands accept parameters from frontend and return `Result<T, String>`
   - Error handling uses `anyhow::Result` internally, converted to `String` for Tauri

   ```rust
   #[tauri::command]
   pub async fn my_command(
       app: AppHandle,
       param: String,
   ) -> Result<ReturnType, String> {
       // Implementation
       Ok(result)
   }
   ```

4. **State Management**
   - Global state managed via Tauri's state management (`app.manage()`)
   - Use `Arc<Mutex<T>>` for thread-safe shared state
   - Key state managers: `ClaudeProcessState`, `CheckpointState`, `ProcessRegistryState`, `AgentDb`

---

## Development Workflows

### Understanding the Build System

opcode uses an **unusual Tauri workflow**:

1. **Frontend must be built FIRST** before running Tauri
2. The `beforeDevCommand` in `tauri.conf.json` is **intentionally empty**
3. This is **NOT** a hot-reload dev setup - you build once, then run
4. Rust code watches and recompiles automatically during `tauri dev`

### Standard Development Workflow

#### Option 1: Manual Commands (Recommended for beginners)

```bash
# 1. Build the frontend
bun run build

# 2. Start Tauri dev server (watches Rust files)
bun run tauri dev
```

#### Option 2: Using Just (Recommended for advanced users)

```bash
# Quick start: build frontend + run app
just dev      # or just quick

# Build everything from scratch
just build

# Clean all build artifacts
just clean
```

#### Option 3: Using npm/bun Scripts

```bash
# Build frontend only
bun run build

# Type-check TypeScript
bun run check

# Start Tauri dev
bun run tauri dev
```

### Frontend-Only Development

If you're only working on frontend changes and don't need Tauri:

```bash
# Start Vite dev server (port 1420)
bun run dev

# Open browser to http://localhost:1420
# Note: Tauri APIs won't work in browser mode
```

### Backend-Only Development

If you're only working on Rust code:

```bash
cd src-tauri

# Check for compilation errors
cargo check

# Run Rust tests
cargo test

# Format code
cargo fmt

# Lint with Clippy
cargo clippy

# Build release version
cargo build --release
```

### Web Server Mode Development

opcode includes a web server mode for mobile/browser access:

```bash
# Build frontend first
bun run build

# Run web server (port 8080 by default)
just web

# Or run with custom port
just web-port 3000

# Get your local IP for phone access
just ip
```

**Important**: Web server mode has known issues with multi-user sessions (see `web_server.design.md`).

### Full Build Cycle

```bash
# Clean everything
just clean

# Install dependencies
bun install

# Build frontend
bun run build

# Build backend (debug)
cd src-tauri && cargo build

# Or build backend (release)
cd src-tauri && cargo build --release

# Run the application
bun run tauri dev
```

---

## Adding New Features

### Step-by-Step Feature Development

#### 1. Planning Phase

- Review existing code to understand patterns
- Check `CONTRIBUTING.md` for guidelines
- Create a GitHub issue describing the feature
- Discuss approach with maintainers (if major feature)

#### 2. Frontend Feature (React Component)

**Example: Adding a New Settings Panel**

1. **Create the Component**

   ```bash
   # Create component file
   touch src/components/NewSettingsPanel.tsx
   ```

2. **Implement the Component**

   ```typescript
   import React, { useState, useEffect } from "react";
   import { Button } from "@/components/ui/button";
   import { Input } from "@/components/ui/input";
   import { Label } from "@/components/ui/label";
   import { api } from "@/lib/api";

   interface NewSettingsPanelProps {
     onSave?: () => void;
   }

   export function NewSettingsPanel({ onSave }: NewSettingsPanelProps) {
     const [setting, setSetting] = useState("");
     const [loading, setLoading] = useState(false);

     const handleSave = async () => {
       setLoading(true);
       try {
         await api.saveNewSetting(setting);
         onSave?.();
       } catch (error) {
         console.error("Failed to save setting:", error);
       } finally {
         setLoading(false);
       }
     };

     return (
       <div className="space-y-4">
         <div>
           <Label htmlFor="setting">New Setting</Label>
           <Input
             id="setting"
             value={setting}
             onChange={(e) => setSetting(e.target.value)}
             placeholder="Enter value"
           />
         </div>
         <Button onClick={handleSave} disabled={loading}>
           {loading ? "Saving..." : "Save"}
         </Button>
       </div>
     );
   }
   ```

3. **Add Types** (if needed)

   Update `src/lib/api.ts`:

   ```typescript
   export interface NewSettingType {
     key: string;
     value: string;
   }

   // Add to API object
   saveNewSetting: async (value: string): Promise<void> => {
     return apiCall("save_new_setting", { value });
   }
   ```

4. **Integrate Component**

   Add to parent component (e.g., `Settings.tsx`):

   ```typescript
   import { NewSettingsPanel } from "./NewSettingsPanel";

   // Inside render:
   <NewSettingsPanel onSave={handleSettingsSaved} />
   ```

5. **Test in Browser**

   ```bash
   bun run build
   bun run tauri dev
   ```

#### 3. Backend Feature (Tauri Command)

**Example: Adding a New Tauri Command**

1. **Determine Command Module**

   Choose appropriate module in `src-tauri/src/commands/`:
   - `agents.rs` - Agent-related commands
   - `claude.rs` - Claude Code CLI commands
   - `mcp.rs` - MCP server commands
   - `storage.rs` - Database operations
   - `usage.rs` - Usage tracking
   - Create new module if needed

2. **Implement the Command**

   Add to `src-tauri/src/commands/my_feature.rs`:

   ```rust
   use tauri::{AppHandle, Emitter};
   use anyhow::{Context, Result};
   use serde::{Deserialize, Serialize};

   #[derive(Debug, Serialize, Deserialize)]
   pub struct NewFeatureRequest {
       pub parameter: String,
   }

   #[derive(Debug, Serialize, Deserialize)]
   pub struct NewFeatureResponse {
       pub result: String,
   }

   /// Command to perform new feature operation
   #[tauri::command]
   pub async fn perform_new_feature(
       app: AppHandle,
       request: NewFeatureRequest,
   ) -> Result<NewFeatureResponse, String> {
       // Implementation
       let result = process_feature(&request.parameter)
           .await
           .map_err(|e| format!("Failed to perform feature: {}", e))?;

       // Emit event if needed
       app.emit("new-feature-completed", &result)
           .map_err(|e| e.to_string())?;

       Ok(NewFeatureResponse { result })
   }

   async fn process_feature(param: &str) -> Result<String> {
       // Business logic here
       Ok(format!("Processed: {}", param))
   }
   ```

3. **Export Command**

   Update `src-tauri/src/commands/mod.rs`:

   ```rust
   pub mod my_feature;

   // Re-export for convenience
   pub use my_feature::{perform_new_feature, NewFeatureRequest, NewFeatureResponse};
   ```

4. **Register Command**

   Update `src-tauri/src/main.rs`:

   ```rust
   use commands::my_feature::perform_new_feature;

   fn main() {
       tauri::Builder::default()
           // ... other plugins
           .invoke_handler(tauri::generate_handler![
               // ... existing commands
               perform_new_feature,
           ])
           .run(tauri::generate_context!())
           .expect("error while running tauri application");
   }
   ```

5. **Add Frontend API Wrapper**

   Update `src/lib/api.ts`:

   ```typescript
   performNewFeature: async (parameter: string): Promise<NewFeatureResponse> => {
     return apiCall<NewFeatureResponse>("perform_new_feature", {
       parameter,
     });
   }
   ```

6. **Test the Command**

   ```bash
   cd src-tauri
   cargo test my_feature
   cargo build
   cd ..
   bun run build
   bun run tauri dev
   ```

#### 4. Adding a New Rust Module

**Example: Creating a New Feature Module**

1. **Create Module Files**

   ```bash
   mkdir src-tauri/src/my_module
   touch src-tauri/src/my_module/mod.rs
   touch src-tauri/src/my_module/logic.rs
   ```

2. **Implement Module**

   `src-tauri/src/my_module/mod.rs`:

   ```rust
   pub mod logic;

   pub use logic::{MyType, process_something};
   ```

   `src-tauri/src/my_module/logic.rs`:

   ```rust
   use anyhow::Result;

   pub struct MyType {
       pub data: String,
   }

   pub fn process_something(input: &str) -> Result<String> {
       Ok(format!("Processed: {}", input))
   }
   ```

3. **Export Module**

   Update `src-tauri/src/lib.rs`:

   ```rust
   pub mod my_module;
   ```

4. **Use in Commands**

   ```rust
   use crate::my_module::{MyType, process_something};

   #[tauri::command]
   pub async fn use_my_module(input: String) -> Result<String, String> {
       process_something(&input).map_err(|e| e.to_string())
   }
   ```

---

## Testing Guidelines

### Frontend Testing

Currently, opcode **does not have a formal frontend test suite**. However, here are recommended practices:

#### Manual Testing Checklist

1. **Component Rendering**
   - Verify component renders without errors
   - Check responsive design (resize window)
   - Test light/dark theme switching

2. **User Interactions**
   - Test all buttons and inputs
   - Verify form validation
   - Check loading states

3. **API Integration**
   - Test API calls with valid data
   - Test error handling with invalid data
   - Verify loading/error states

4. **Browser Console**
   - Check for console errors/warnings
   - Verify analytics events (if applicable)

#### Future Testing Setup (Recommended)

```bash
# Install testing libraries (not yet configured)
bun add -d vitest @testing-library/react @testing-library/jest-dom
bun add -d @testing-library/user-event jsdom

# Future test command
bun test
```

### Backend Testing (Rust)

#### Running Tests

```bash
cd src-tauri

# Run all tests
cargo test

# Run tests with output
cargo test -- --nocapture

# Run specific test
cargo test test_name

# Run tests in specific module
cargo test commands::agents::tests
```

#### Writing Tests

**Example: Unit Test**

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_process_feature() {
        let result = process_feature("test").unwrap();
        assert_eq!(result, "Processed: test");
    }

    #[tokio::test]
    async fn test_async_function() {
        let result = async_function().await.unwrap();
        assert!(result.is_valid());
    }
}
```

**Example: Integration Test**

Create `src-tauri/tests/integration_test.rs`:

```rust
use opcode_lib::my_module::process_something;

#[test]
fn test_integration() {
    let result = process_something("integration test").unwrap();
    assert!(result.contains("integration test"));
}
```

#### Test Coverage

```bash
# Install tarpaulin (once)
cargo install cargo-tarpaulin

# Run with coverage
cargo tarpaulin --out Html

# Open coverage report
open tarpaulin-report.html
```

### CI/CD Testing

The project uses GitHub Actions for automated testing:

- **PR Checks** (`.github/workflows/pr-check.yml`)
  - Runs `bun run check` (TypeScript + Rust check)
  - Validates on every PR

- **Build Tests** (`.github/workflows/build-test.yml`)
  - Full build validation for Linux and macOS
  - Runs on every push

---

## Debugging Techniques

### Frontend Debugging

#### Browser DevTools

1. **Start Dev Server**
   ```bash
   bun run dev
   ```

2. **Open DevTools**
   - Chrome/Edge: `F12` or `Cmd+Option+I` (Mac)
   - Firefox: `F12` or `Cmd+Option+I` (Mac)

3. **Key DevTools Features**
   - **Console**: View logs, errors, API responses
   - **Network**: Inspect API calls (in web mode only)
   - **Sources**: Set breakpoints in TypeScript code
   - **React DevTools**: Inspect component tree and state

#### Tauri DevTools

When running in Tauri mode:

1. **Open DevTools in Tauri**
   ```bash
   bun run tauri dev
   # DevTools should open automatically in development mode
   ```

2. **If DevTools don't open**, add to `tauri.conf.json`:
   ```json
   {
     "app": {
       "withGlobalTauri": true
     }
   }
   ```

#### Debugging API Calls

Add logging to `src/lib/apiAdapter.ts`:

```typescript
export async function apiCall<T>(command: string, args?: any): Promise<T> {
  console.log(`[API] Calling ${command} with args:`, args);

  try {
    const result = await invoke<T>(command, args);
    console.log(`[API] ${command} result:`, result);
    return result;
  } catch (error) {
    console.error(`[API] ${command} error:`, error);
    throw error;
  }
}
```

#### React Component Debugging

```typescript
import React, { useEffect } from "react";

export function MyComponent() {
  // Debug props and state
  useEffect(() => {
    console.log("[MyComponent] Props:", props);
    console.log("[MyComponent] State:", state);
  }, [props, state]);

  // Debug renders
  console.log("[MyComponent] Rendering with:", { props, state });

  return <div>...</div>;
}
```

### Backend Debugging

#### Logging

opcode uses `env_logger` for Rust logging.

1. **Enable Logging**
   ```bash
   export RUST_LOG=debug
   bun run tauri dev

   # Or for specific modules
   export RUST_LOG=opcode::commands::claude=debug
   ```

2. **Add Logs to Code**
   ```rust
   use log::{debug, info, warn, error};

   #[tauri::command]
   pub async fn my_command(param: String) -> Result<String, String> {
       info!("my_command called with: {}", param);
       debug!("Detailed debug info: {:?}", param);

       // ... code

       if error_condition {
           error!("Something went wrong!");
       }

       Ok(result)
   }
   ```

3. **Log Levels**
   - `error!`: Critical errors
   - `warn!`: Warnings
   - `info!`: Important information
   - `debug!`: Detailed debugging
   - `trace!`: Very detailed tracing

#### Rust Debugger (LLDB/GDB)

1. **Build with Debug Symbols**
   ```bash
   cd src-tauri
   cargo build
   ```

2. **Run with Debugger (VS Code)**

   Create `.vscode/launch.json`:
   ```json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "type": "lldb",
         "request": "launch",
         "name": "Debug Tauri",
         "cargo": {
           "args": ["build", "--bin=opcode"],
           "filter": {
             "name": "opcode",
             "kind": "bin"
           }
         },
         "args": [],
         "cwd": "${workspaceFolder}/src-tauri"
       }
     ]
   }
   ```

3. **Set Breakpoints**
   - Click in the gutter next to line numbers
   - Use `F5` to start debugging

#### Debugging Tauri Commands

Add `dbg!` macro for quick debugging:

```rust
#[tauri::command]
pub async fn my_command(param: String) -> Result<String, String> {
    dbg!(&param);  // Prints to stderr

    let intermediate = process(param);
    dbg!(&intermediate);

    Ok(intermediate)
}
```

#### Debugging Process Execution

When debugging Claude Code process execution:

```rust
use std::process::{Command, Stdio};

let mut child = Command::new("claude")
    .args(&["code", project_path])
    .stdin(Stdio::piped())
    .stdout(Stdio::piped())
    .stderr(Stdio::piped())
    .spawn()
    .map_err(|e| {
        eprintln!("Failed to spawn Claude process: {}", e);
        e.to_string()
    })?;

// Read stdout/stderr for debugging
let stdout = child.stdout.take().unwrap();
let reader = BufReader::new(stdout);
for line in reader.lines() {
    eprintln!("[Claude stdout] {}", line.unwrap());
}
```

### Performance Profiling

#### Frontend Profiling

1. **React DevTools Profiler**
   - Open React DevTools
   - Go to "Profiler" tab
   - Click "Record"
   - Perform actions
   - Click "Stop"
   - Analyze component render times

2. **Chrome Performance Tab**
   - Open DevTools → Performance tab
   - Click "Record"
   - Perform actions
   - Click "Stop"
   - Analyze flame graph

#### Backend Profiling

```bash
# Install cargo-flamegraph
cargo install flamegraph

# Generate flamegraph
cd src-tauri
cargo flamegraph --bin opcode

# Open flamegraph.svg in browser
```

---

## Hot Reload Behavior

### Important: NO Hot Reload for Frontend

opcode uses an **unusual Tauri workflow**:

- **Frontend changes require a full rebuild**: `bun run build`
- **NOT a live hot-reload setup**
- This is intentional based on project design

### Workflow for Frontend Changes

```bash
# Make changes to React components in src/

# Rebuild frontend
bun run build

# If tauri dev is running, it will automatically reload
# If not, restart tauri dev
bun run tauri dev
```

### Hot Reload for Backend (Rust)

**Rust changes DO have hot reload**:

- When running `bun run tauri dev`, Tauri watches Rust files
- Any changes to `src-tauri/src/**/*.rs` trigger automatic recompilation
- The app restarts automatically after successful compilation

```bash
# Start Tauri dev (watches Rust files)
bun run tauri dev

# Make changes to src-tauri/src/commands/my_command.rs
# Save file → Tauri automatically recompiles → App restarts
```

### Alternative: Vite Dev Server (Frontend Only)

For rapid frontend-only iteration (without Tauri):

```bash
# Start Vite dev server (hot reload enabled)
bun run dev

# Open http://localhost:1420 in browser
# Changes to React components hot reload instantly
```

**Note**: Tauri APIs (`@tauri-apps/api`) won't work in browser mode.

---

## Performance Optimization

### Frontend Performance

#### 1. Code Splitting

The project already uses manual code splitting in `vite.config.ts`:

```typescript
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'react-vendor': ['react', 'react-dom'],
        'ui-vendor': [...], // Radix UI components
        'editor-vendor': ['@uiw/react-md-editor'],
        'tauri': ['@tauri-apps/api', ...],
      },
    },
  },
}
```

**When adding new heavy dependencies**, update this config.

#### 2. Component Optimization

**Use React.memo for expensive renders**:

```typescript
import React, { memo } from "react";

interface ExpensiveComponentProps {
  data: LargeDataType;
}

export const ExpensiveComponent = memo(({ data }: ExpensiveComponentProps) => {
  // Expensive rendering logic
  return <div>...</div>;
});
```

**Use useCallback for stable function references**:

```typescript
import { useCallback } from "react";

const handleClick = useCallback(() => {
  performExpensiveOperation();
}, [dependencies]);
```

**Use useMemo for expensive computations**:

```typescript
import { useMemo } from "react";

const sortedData = useMemo(() => {
  return data.sort((a, b) => a.value - b.value);
}, [data]);
```

#### 3. Virtualization for Long Lists

The project uses `@tanstack/react-virtual` for long lists:

```typescript
import { useVirtualizer } from "@tanstack/react-virtual";

const parentRef = useRef<HTMLDivElement>(null);

const virtualizer = useVirtualizer({
  count: items.length,
  getScrollElement: () => parentRef.current,
  estimateSize: () => 50,
  overscan: 5,
});

return (
  <div ref={parentRef} style={{ height: "500px", overflow: "auto" }}>
    <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
      {virtualizer.getVirtualItems().map((virtualItem) => (
        <div key={virtualItem.key} style={{
          position: "absolute",
          top: `${virtualItem.start}px`,
          height: `${virtualItem.size}px`,
        }}>
          {items[virtualItem.index]}
        </div>
      ))}
    </div>
  </div>
);
```

#### 4. Lazy Loading

```typescript
import { lazy, Suspense } from "react";

const HeavyComponent = lazy(() => import("./HeavyComponent"));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <HeavyComponent />
    </Suspense>
  );
}
```

### Backend Performance

#### 1. Async/Await Properly

```rust
use tokio::task;

#[tauri::command]
pub async fn parallel_operations() -> Result<Vec<String>, String> {
    // Run operations in parallel
    let (result1, result2, result3) = tokio::join!(
        operation1(),
        operation2(),
        operation3(),
    );

    Ok(vec![result1?, result2?, result3?])
}
```

#### 2. Database Connection Pooling

```rust
// Reuse database connections
pub struct AppState {
    db_pool: Arc<Mutex<rusqlite::Connection>>,
}

#[tauri::command]
pub async fn db_operation(state: tauri::State<'_, AppState>) -> Result<(), String> {
    let conn = state.db_pool.lock().map_err(|e| e.to_string())?;
    // Use connection
    Ok(())
}
```

#### 3. Avoid Blocking Operations

```rust
use tokio::task::spawn_blocking;

#[tauri::command]
pub async fn heavy_computation(data: Vec<u8>) -> Result<String, String> {
    // Move blocking computation to thread pool
    let result = spawn_blocking(move || {
        // CPU-intensive work here
        expensive_computation(data)
    })
    .await
    .map_err(|e| e.to_string())?;

    Ok(result)
}
```

#### 4. Use Efficient Data Structures

```rust
use std::collections::HashMap;

// Use HashMap for O(1) lookups instead of Vec with O(n) searches
let mut lookup: HashMap<String, Value> = HashMap::new();
```

#### 5. Profile and Optimize

```bash
# Use cargo flamegraph to identify bottlenecks
cd src-tauri
cargo flamegraph --bin opcode

# Use cargo bench for benchmarking
cargo bench
```

---

## Code Style Guidelines

### TypeScript/React Style

#### General Principles

- **Functional components with hooks** (no class components)
- **TypeScript strict mode** (configured in `tsconfig.json`)
- **Explicit types** for props and return values
- **Destructure props** in function signatures

#### Formatting

The project uses **TypeScript strict mode** without explicit Prettier config:

- **Indentation**: 2 spaces
- **Semicolons**: Required
- **Quotes**: Double quotes for strings
- **Line length**: Aim for 80-100 characters

#### Component Structure

```typescript
import React, { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { api, type MyType } from "@/lib/api";

interface MyComponentProps {
  /** Description of prop */
  title: string;
  /** Optional callback */
  onSave?: (data: MyType) => void;
}

/**
 * MyComponent provides functionality for...
 *
 * @param props - Component props
 */
export function MyComponent({ title, onSave }: MyComponentProps) {
  // State declarations
  const [data, setData] = useState<MyType | null>(null);
  const [loading, setLoading] = useState(false);

  // Effects
  useEffect(() => {
    loadData();
  }, []);

  // Callbacks
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const result = await api.getData();
      setData(result);
    } catch (error) {
      console.error("Failed to load data:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Event handlers
  const handleSave = () => {
    if (data) {
      onSave?.(data);
    }
  };

  // Early returns for loading/error states
  if (loading) {
    return <div>Loading...</div>;
  }

  if (!data) {
    return <div>No data</div>;
  }

  // Main render
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">{title}</h2>
      <div>{data.content}</div>
      <Button onClick={handleSave}>Save</Button>
    </div>
  );
}
```

#### Naming Conventions

- **Components**: PascalCase (e.g., `ClaudeCodeSession`)
- **Files**: PascalCase for components (e.g., `ClaudeCodeSession.tsx`)
- **Functions**: camelCase (e.g., `handleSubmit`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- **Types/Interfaces**: PascalCase (e.g., `SessionProps`)

#### Import Aliases

Use `@/` for absolute imports (configured in `tsconfig.json` and `vite.config.ts`):

```typescript
// Good
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";

// Avoid
import { Button } from "../../components/ui/button";
```

#### Tailwind CSS Classes

Use `cn()` utility for conditional classes:

```typescript
import { cn } from "@/lib/utils";

<div className={cn(
  "base-classes",
  isActive && "active-classes",
  isError && "error-classes"
)} />
```

### Rust Style

#### General Principles

- Follow **Rust standard conventions** (enforced by `cargo fmt` and `cargo clippy`)
- **Explicit error handling** with `Result` and `?` operator
- **Descriptive variable names** (no abbreviations unless obvious)
- **Comprehensive documentation** with `///` comments

#### Formatting

Run `cargo fmt` before committing:

```bash
cd src-tauri
cargo fmt
```

#### Code Structure

```rust
use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Emitter};

/// Request structure for my_command
#[derive(Debug, Serialize, Deserialize)]
pub struct MyRequest {
    /// The input parameter
    pub input: String,
}

/// Response structure for my_command
#[derive(Debug, Serialize, Deserialize)]
pub struct MyResponse {
    /// The result of the operation
    pub result: String,
}

/// Performs a specific operation based on the request
///
/// # Arguments
///
/// * `app` - The Tauri application handle
/// * `request` - The request parameters
///
/// # Returns
///
/// * `Result<MyResponse, String>` - The operation result or error
///
/// # Errors
///
/// Returns an error if the operation fails
#[tauri::command]
pub async fn my_command(
    app: AppHandle,
    request: MyRequest,
) -> Result<MyResponse, String> {
    // Implementation
    let result = process_request(&request)
        .await
        .map_err(|e| format!("Failed to process request: {}", e))?;

    // Emit event
    app.emit("command-completed", &result)
        .map_err(|e| e.to_string())?;

    Ok(MyResponse { result })
}

/// Internal function to process the request
async fn process_request(request: &MyRequest) -> Result<String> {
    // Business logic
    Ok(format!("Processed: {}", request.input))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_process_request() {
        let request = MyRequest {
            input: "test".to_string(),
        };
        let result = process_request(&request).await.unwrap();
        assert_eq!(result, "Processed: test");
    }
}
```

#### Naming Conventions

- **Functions**: snake_case (e.g., `execute_claude_code`)
- **Types**: PascalCase (e.g., `ClaudeProcessState`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRY_COUNT`)
- **Modules**: snake_case (e.g., `claude_binary`)

#### Error Handling

**Use `anyhow::Result` internally**:

```rust
use anyhow::{Context, Result};

fn internal_function() -> Result<String> {
    let data = read_file("path.txt")
        .context("Failed to read config file")?;

    let parsed = parse_data(&data)
        .context("Failed to parse data")?;

    Ok(parsed)
}
```

**Convert to `String` for Tauri commands**:

```rust
#[tauri::command]
pub async fn public_command() -> Result<String, String> {
    internal_function()
        .map_err(|e| format!("Command failed: {}", e))
}
```

#### Linting

Run `cargo clippy` regularly:

```bash
cd src-tauri
cargo clippy
```

Fix all clippy warnings before committing.

---

## Git Workflow

### Branching Strategy

- **main**: Stable production branch
- **Feature branches**: `feature/your-feature-name`
- **Bug fixes**: `fix/issue-description`
- **Refactoring**: `refactor/what-changed`
- **Documentation**: `docs/what-docs`

### Branch Naming

```bash
# Examples
git checkout -b feature/add-custom-prompts
git checkout -b fix/session-list-scrolling
git checkout -b refactor/api-adapter
git checkout -b docs/development-guide
```

### Commit Message Conventions

Follow the convention from `CONTRIBUTING.md`:

**Format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring (no functional changes)
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, etc.
- `style`: Formatting, whitespace (not CSS)

**Examples**:
```bash
# Good commits
git commit -m "feat(agents): add custom timeout configuration"
git commit -m "fix(session): resolve scrolling issue in session list"
git commit -m "docs: update development workflow guide"
git commit -m "refactor(api): simplify error handling in apiAdapter"
git commit -m "perf(frontend): add virtualization to project list"

# Bad commits (avoid)
git commit -m "fix stuff"
git commit -m "WIP"
git commit -m "Update code"
```

**Multi-line commits**:
```bash
git commit -m "feat(checkpoints): add automatic checkpoint creation

- Implement auto-checkpoint on every 10 messages
- Add configuration UI for checkpoint interval
- Store checkpoint settings in database

Closes #123"
```

### Git Workflow Steps

1. **Update main branch**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

3. **Make changes and commit frequently**
   ```bash
   # Stage changes
   git add src/components/MyComponent.tsx
   git add src/lib/api.ts

   # Commit with descriptive message
   git commit -m "feat(components): add MyComponent with API integration"
   ```

4. **Keep branch updated with main**
   ```bash
   git checkout main
   git pull origin main
   git checkout feature/my-feature
   git rebase main

   # Or merge (if rebase is problematic)
   git merge main
   ```

5. **Push to remote**
   ```bash
   git push origin feature/my-feature
   ```

6. **Create Pull Request** (see next section)

### Before Committing

**Run checks**:
```bash
# Frontend type check
bun run check

# Backend checks
cd src-tauri
cargo fmt      # Format Rust code
cargo clippy   # Lint Rust code
cargo test     # Run tests
cd ..

# Full build test
bun run build
bun run tauri build --debug
```

### Handling Merge Conflicts

```bash
# If rebase has conflicts
git rebase main

# Git will show conflicted files
# Edit files to resolve conflicts
# Look for conflict markers: <<<<<<<, =======, >>>>>>>

# After resolving conflicts
git add <resolved-file>
git rebase --continue

# If you want to abort the rebase
git rebase --abort
```

---

## Pull Request Process

### Before Creating a PR

1. **Ensure branch is up-to-date**
   ```bash
   git checkout main
   git pull origin main
   git checkout your-branch
   git rebase main
   ```

2. **Run all checks**
   ```bash
   bun run check
   cd src-tauri && cargo fmt && cargo clippy && cargo test
   ```

3. **Test manually**
   - Build and run the application
   - Test your feature thoroughly
   - Test edge cases and error scenarios

### Creating the PR

1. **Push your branch**
   ```bash
   git push origin your-branch
   ```

2. **Open PR on GitHub**
   - Go to [https://github.com/getAsterisk/opcode/pulls](https://github.com/getAsterisk/opcode/pulls)
   - Click "New Pull Request"
   - Select your branch

3. **Write PR Title** (following `CONTRIBUTING.md`):
   ```
   Feature: added custom agent timeout configuration
   Fix: resolved session list scrolling issue
   Docs: updated development workflow guide
   Refactor: simplified API error handling
   Improve: optimized project list rendering
   ```

4. **Write PR Description**:

   ```markdown
   ## Summary

   Brief description of what this PR does.

   ## Changes

   - Added feature X
   - Fixed bug Y
   - Updated documentation Z

   ## Testing

   - [ ] Tested on macOS
   - [ ] Tested on Linux
   - [ ] Tested on Windows (if applicable)
   - [ ] Added/updated tests
   - [ ] Manual testing completed

   ## Screenshots (if applicable)

   [Add screenshots or GIFs showing the changes]

   ## Related Issues

   Closes #123
   Relates to #456
   ```

### PR Review Process

1. **Automated Checks**
   - CI runs `bun run check` (TypeScript + Rust check)
   - Build tests run for Linux and macOS
   - All checks must pass

2. **Code Review**
   - Maintainers review your code
   - Address feedback by pushing new commits
   - Engage in discussion about design decisions

3. **Addressing Feedback**
   ```bash
   # Make requested changes
   git add changed-files
   git commit -m "refactor: address PR feedback"
   git push origin your-branch
   ```

4. **After Approval**
   - Maintainer will merge your PR
   - Your branch will be deleted
   - Celebrate! 🎉

### PR Best Practices

- **Keep PRs focused**: One feature/fix per PR
- **Keep PRs small**: Easier to review (aim for <500 lines changed)
- **Write clear descriptions**: Help reviewers understand your changes
- **Respond to feedback promptly**: Engage in constructive discussion
- **Test thoroughly**: Don't rely solely on reviewers to find bugs
- **Update documentation**: If your change affects docs, update them

---

## Common Pitfalls

### Frontend Pitfalls

#### 1. Forgetting to Rebuild Frontend

**Problem**: Made React changes, but they don't appear in Tauri app.

**Solution**:
```bash
bun run build
```

**Why**: opcode doesn't have hot-reload for frontend. You must rebuild manually.

#### 2. Using Tauri APIs in Browser Mode

**Problem**: `window.__TAURI__` is undefined when running `bun run dev`.

**Solution**: Use the API adapter (`apiAdapter.ts`) which handles both Tauri and web modes:
```typescript
import { api } from "@/lib/api";

// Good: Works in both modes
const projects = await api.listProjects();

// Bad: Only works in Tauri mode
import { invoke } from "@tauri-apps/api/core";
const projects = await invoke("list_projects");
```

#### 3. Not Handling Loading States

**Problem**: UI shows stale data while loading.

**Solution**: Always handle loading states:
```typescript
const [data, setData] = useState(null);
const [loading, setLoading] = useState(false);

useEffect(() => {
  setLoading(true);
  api.getData()
    .then(setData)
    .finally(() => setLoading(false));
}, []);

if (loading) return <div>Loading...</div>;
if (!data) return <div>No data</div>;
```

#### 4. Memory Leaks with Event Listeners

**Problem**: Event listeners not cleaned up.

**Solution**: Always return cleanup function:
```typescript
useEffect(() => {
  const unlisten = await listen("my-event", (event) => {
    handleEvent(event.payload);
  });

  return () => {
    unlisten();  // Cleanup
  };
}, []);
```

### Backend Pitfalls

#### 1. Not Using `?` Operator

**Problem**: Verbose error handling.

**Bad**:
```rust
match result {
    Ok(value) => value,
    Err(e) => return Err(e.to_string()),
}
```

**Good**:
```rust
let value = result?;
```

#### 2. Blocking Tokio Runtime

**Problem**: Using blocking operations in async context.

**Bad**:
```rust
#[tauri::command]
pub async fn heavy_work() -> Result<String, String> {
    std::thread::sleep(Duration::from_secs(10));  // Blocks executor!
    Ok("Done".to_string())
}
```

**Good**:
```rust
use tokio::task::spawn_blocking;

#[tauri::command]
pub async fn heavy_work() -> Result<String, String> {
    spawn_blocking(|| {
        std::thread::sleep(Duration::from_secs(10));
        "Done".to_string()
    })
    .await
    .map_err(|e| e.to_string())
}
```

#### 3. Not Handling Mutex Poisoning

**Problem**: Panic when mutex is poisoned.

**Good**:
```rust
let guard = state.lock().map_err(|e| {
    error!("Mutex poisoned: {}", e);
    "Internal error: mutex poisoned".to_string()
})?;
```

#### 4. Forgetting to Register Commands

**Problem**: Added new command but forgot to register it in `main.rs`.

**Solution**: Always update `main.rs`:
```rust
.invoke_handler(tauri::generate_handler![
    // ... existing commands
    my_new_command,  // Don't forget!
])
```

#### 5. Not Converting Errors for Tauri

**Problem**: Returning `anyhow::Error` from Tauri commands.

**Bad**:
```rust
#[tauri::command]
pub async fn my_command() -> Result<String> {  // Wrong return type!
    Ok("value".to_string())
}
```

**Good**:
```rust
#[tauri::command]
pub async fn my_command() -> Result<String, String> {  // Correct!
    internal_function()
        .map_err(|e| e.to_string())
}
```

### Build Pitfalls

#### 1. Multiple Binaries Error

**Problem**: `cargo run` complains about multiple binaries.

**Solution**: Already fixed in `Cargo.toml` with `default-run = "opcode"`.

If issue persists:
```bash
cargo run --bin opcode
```

#### 2. `dist/` Not Found Error

**Problem**: `tauri dev` fails with "frontendDist doesn't exist".

**Solution**:
```bash
bun run build
```

#### 3. Cargo Environment Not Loaded

**Problem**: `cargo not found` error.

**Solution**:
```bash
source "$HOME/.cargo/env"
# Or add to shell profile and restart terminal
```

---

## Release Process

### Versioning

opcode uses **semantic versioning** (SemVer):

- **Major**: Breaking changes (e.g., `1.0.0` → `2.0.0`)
- **Minor**: New features (e.g., `0.2.0` → `0.3.0`)
- **Patch**: Bug fixes (e.g., `0.2.1` → `0.2.2`)

### Release Checklist

1. **Update Version Numbers**

   Update in 3 places:

   ```bash
   # package.json
   {
     "version": "0.3.0"
   }

   # src-tauri/Cargo.toml
   [package]
   version = "0.3.0"

   # src-tauri/tauri.conf.json
   {
     "version": "0.3.0"
   }
   ```

2. **Update CHANGELOG**

   Create/update `CHANGELOG.md`:
   ```markdown
   ## [0.3.0] - 2025-01-15

   ### Added
   - Feature X
   - Feature Y

   ### Fixed
   - Bug A
   - Bug B

   ### Changed
   - Improvement C
   ```

3. **Run Full Test Suite**
   ```bash
   bun run check
   cd src-tauri && cargo test && cargo clippy
   ```

4. **Build and Test Locally**
   ```bash
   bun run tauri build

   # Test the built executable
   ./src-tauri/target/release/opcode
   ```

5. **Commit Version Bump**
   ```bash
   git add package.json src-tauri/Cargo.toml src-tauri/tauri.conf.json CHANGELOG.md
   git commit -m "chore: bump version to 0.3.0"
   git push origin main
   ```

6. **Create Git Tag**
   ```bash
   git tag -a v0.3.0 -m "Release v0.3.0"
   git push origin v0.3.0
   ```

7. **GitHub Release Workflow Triggers**

   The tag push triggers `.github/workflows/release.yml`:
   - Builds Linux artifacts (`.deb`, `.AppImage`)
   - Builds macOS artifacts (`.dmg`, `.app`)
   - Creates GitHub release (draft)
   - Uploads all artifacts

8. **Finalize GitHub Release**

   - Go to [Releases](https://github.com/getAsterisk/opcode/releases)
   - Find the draft release
   - Review auto-generated release notes
   - Edit description if needed
   - Publish release

### Manual Release Build (if needed)

```bash
# Build for current platform
bun run tauri build

# Build specific target (macOS Universal)
bun run tauri build --target universal-apple-darwin

# Build DMG only (macOS)
bun run build:dmg

# Artifacts location
# Linux: src-tauri/target/release/bundle/deb/, .appimage/
# macOS: src-tauri/target/release/bundle/dmg/, macos/
# Windows: src-tauri/target/release/bundle/msi/, nsis/
```

### Post-Release

1. **Announce on Discord** (if applicable)
2. **Update documentation** with new features
3. **Close related GitHub issues/PRs**

---

## Additional Resources

### Documentation

- [README.md](/Users/max/local/opcode/README.md) - Project overview
- [CONTRIBUTING.md](/Users/max/local/opcode/CONTRIBUTING.md) - Contribution guidelines
- [CLAUDE.md](/Users/max/local/opcode/CLAUDE.md) - Claude Code-specific instructions
- [docs/](/Users/max/local/opcode/docs/) - Additional documentation

### External Resources

- [Tauri Documentation](https://tauri.app/v2/guides/)
- [React Documentation](https://react.dev/)
- [Rust Book](https://doc.rust-lang.org/book/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)

### Community

- [GitHub Issues](https://github.com/getAsterisk/opcode/issues)
- [GitHub Discussions](https://github.com/getAsterisk/opcode/discussions)
- [Discord](https://discord.com/invite/KYwhHVzUsY)

---

## Conclusion

This guide covers the essential workflows for developing opcode. As you become more familiar with the codebase, you'll discover additional patterns and best practices.

**Key Takeaways**:

1. **Frontend changes require rebuild**: No hot-reload for React
2. **Rust changes have hot-reload**: Automatic recompilation during `tauri dev`
3. **Use API adapter**: Works in both Tauri and web modes
4. **Follow code style**: TypeScript strict, Rust fmt/clippy
5. **Test thoroughly**: Manual testing + automated checks
6. **Write clear commits**: Follow conventional commit format
7. **Keep PRs focused**: One feature/fix per PR

**Happy coding!** 🚀

If you have questions or need help, don't hesitate to:
- Open a GitHub issue
- Ask in Discord
- Consult the documentation

---

**Last Updated**: 2025-10-20
