# Opcode - Complete Installation Guide

> **A comprehensive, cross-platform installation manual for Opcode**
>
> This guide covers installation for macOS, Linux, and Windows with detailed prerequisites, troubleshooting, and platform-specific instructions.

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
  - [Required Dependencies](#required-dependencies)
  - [Platform-Specific Dependencies](#platform-specific-dependencies)
- [Installation Methods](#installation-methods)
  - [Method 1: Pre-built Releases (Recommended)](#method-1-pre-built-releases-recommended)
  - [Method 2: Build from Source](#method-2-build-from-source)
  - [Method 3: NixOS Installation](#method-3-nixos-installation)
- [Platform-Specific Instructions](#platform-specific-instructions)
  - [macOS Installation](#macos-installation)
  - [Linux Installation](#linux-installation)
  - [Windows Installation](#windows-installation)
- [Post-Installation](#post-installation)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Upgrading](#upgrading)
- [Uninstallation](#uninstallation)
- [Installation History (Original)](#installation-history-original)

---

## System Requirements

### Minimum System Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | macOS 10.15+, Ubuntu 20.04+, Windows 10/11 |
| **Processor** | Intel Core i3 / AMD Ryzen 3 or better, Apple Silicon M1+ |
| **RAM** | 4 GB (8 GB recommended) |
| **Storage** | 1 GB free space (2 GB for development) |
| **Display** | 1280x720 minimum resolution |
| **Internet** | Required for initial setup and Claude Code API |

### Recommended System Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | macOS 12+, Ubuntu 22.04+, Windows 11 |
| **Processor** | Intel Core i5 / AMD Ryzen 5 or better, Apple Silicon M1 Pro+ |
| **RAM** | 8 GB or more |
| **Storage** | 5 GB free space |
| **Display** | 1920x1080 or higher |

### Compatibility Notes

- **macOS**: Universal Binary supports both Intel and Apple Silicon Macs
- **Linux**: Tested on Ubuntu, Debian, Fedora, Arch Linux
- **Windows**: Requires WebView2 (pre-installed on Windows 11)
- **Claude Code CLI**: Must be installed and configured (see [Prerequisites](#prerequisites))

---

## Quick Start

For users who want to get started quickly:

### Pre-built Binaries (Coming Soon)

```bash
# macOS (via Homebrew - coming soon)
brew install opcode

# Linux (AppImage)
chmod +x opcode-*.AppImage
./opcode-*.AppImage

# Windows (MSI Installer - coming soon)
# Download and run opcode-installer.msi
```

**Note**: Pre-built binaries are not yet published. For now, follow [Build from Source](#method-2-build-from-source).

---

## Prerequisites

### Required Dependencies

All platforms require the following:

#### 1. Claude Code CLI

Opcode is a GUI wrapper for Claude Code. You must have the Claude Code CLI installed and configured.

```bash
# Verify Claude Code is installed
claude --version

# If not installed, download from:
# https://claude.ai/code
```

**Installation**:
- Visit [https://claude.ai/code](https://claude.ai/code)
- Download the installer for your platform
- Follow the installation instructions
- Authenticate with your Anthropic account
- Verify with `claude --version`

#### 2. Git

```bash
# Verify Git is installed
git --version

# If not installed:
# macOS: xcode-select --install
# Ubuntu/Debian: sudo apt install git
# Windows: Download from https://git-scm.com
```

---

### Platform-Specific Dependencies

<details>
<summary><b>macOS Dependencies</b></summary>

#### macOS Intel and Apple Silicon

**Required:**
- **Xcode Command Line Tools**: Essential for compilation
  ```bash
  xcode-select --install
  ```

**Optional (for development):**
- **Homebrew**: Package manager for additional tools
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```

- **pkg-config** (recommended):
  ```bash
  brew install pkg-config
  ```

**System Requirements**:
- macOS 10.15 (Catalina) or later
- Minimum 4 GB RAM
- 1 GB free disk space

</details>

<details>
<summary><b>Linux Dependencies (Ubuntu/Debian)</b></summary>

#### Ubuntu 20.04+ / Debian 11+

**Install all required system libraries:**

```bash
sudo apt update
sudo apt install -y \
  pkg-config \
  libwebkit2gtk-4.1-dev \
  libgtk-3-dev \
  libssl-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev \
  build-essential \
  curl \
  wget \
  file \
  libxdo-dev \
  libsoup-3.0-dev \
  libjavascriptcoregtk-4.1-dev \
  patchelf
```

**Alternative for older Ubuntu versions:**

If `libwebkit2gtk-4.1-dev` is not available, use:
```bash
sudo apt install libwebkit2gtk-4.0-dev
```

</details>

<details>
<summary><b>Linux Dependencies (Fedora)</b></summary>

#### Fedora 35+

```bash
sudo dnf install -y \
  pkg-config \
  webkit2gtk4.1-devel \
  gtk3-devel \
  openssl-devel \
  libappindicator-gtk3-devel \
  librsvg2-devel \
  libsoup3-devel \
  javascriptcoregtk4.1-devel \
  patchelf \
  curl \
  wget \
  file
```

</details>

<details>
<summary><b>Linux Dependencies (Arch Linux)</b></summary>

#### Arch Linux

```bash
sudo pacman -S --needed \
  webkit2gtk-4.1 \
  gtk3 \
  openssl \
  libappindicator-gtk3 \
  librsvg \
  libsoup3 \
  base-devel \
  curl \
  wget \
  file \
  patchelf
```

</details>

<details>
<summary><b>Linux Dependencies (NixOS)</b></summary>

#### NixOS

Use the provided `shell.nix` for a complete development environment:

```bash
nix-shell
```

This automatically provides all dependencies. See [Method 3: NixOS Installation](#method-3-nixos-installation).

</details>

<details>
<summary><b>Windows Dependencies</b></summary>

#### Windows 10 / Windows 11

**Required:**

1. **Microsoft C++ Build Tools**
   - Download: [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Install the "Desktop development with C++" workload
   - Minimum components:
     - MSVC v143 - VS 2022 C++ x64/x86 build tools
     - Windows 10 SDK or Windows 11 SDK

2. **WebView2 Runtime**
   - Pre-installed on Windows 11
   - Windows 10: Download from [Microsoft Edge WebView2](https://developer.microsoft.com/microsoft-edge/webview2/)
   - Verify: Check `C:\Program Files (x86)\Microsoft\EdgeWebView\Application`

**Optional:**
- **Git for Windows**: [https://git-scm.com/download/win](https://git-scm.com/download/win)
- **Windows Terminal**: For better command-line experience

**Notes:**
- Restart your terminal after installing Visual Studio Build Tools
- Ensure `cl.exe` is in your PATH (check with `where cl`)

</details>

---

## Installation Methods

### Method 1: Pre-built Releases (Recommended)

**Status**: Pre-built releases coming soon.

When available, download from [GitHub Releases](https://github.com/getAsterisk/opcode/releases):

#### macOS (.dmg)

```bash
# Download the latest release
curl -LO https://github.com/getAsterisk/opcode/releases/latest/download/opcode_macos_universal.dmg

# Open the DMG
open opcode_macos_universal.dmg

# Drag opcode to Applications folder
```

**First Launch:**
- Right-click opcode.app → Open (to bypass Gatekeeper on first launch)
- Or: System Preferences → Security & Privacy → "Open Anyway"

#### Linux (.AppImage)

```bash
# Download the latest release
curl -LO https://github.com/getAsterisk/opcode/releases/latest/download/opcode_linux_x86_64.AppImage

# Make executable
chmod +x opcode_linux_x86_64.AppImage

# Run
./opcode_linux_x86_64.AppImage
```

**Optional: Integrate with system**
```bash
# Move to user bin
mv opcode_linux_x86_64.AppImage ~/.local/bin/opcode

# Create desktop entry
cat > ~/.local/share/applications/opcode.desktop <<EOF
[Desktop Entry]
Type=Application
Name=opcode
Exec=$HOME/.local/bin/opcode
Icon=opcode
Categories=Development;
EOF
```

#### Linux (.deb)

```bash
# Download the latest release
curl -LO https://github.com/getAsterisk/opcode/releases/latest/download/opcode_linux_x86_64.deb

# Install
sudo dpkg -i opcode_linux_x86_64.deb

# Fix dependencies if needed
sudo apt-get install -f

# Run
opcode
```

#### Windows (.msi) - Coming Soon

```powershell
# Download from GitHub Releases
# Double-click the MSI installer
# Follow the installation wizard
```

---

### Method 2: Build from Source

This is the current recommended method until pre-built releases are available.

#### Step 1: Install Rust

**All Platforms:**

```bash
# Install Rust via rustup
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Source the environment (or restart terminal)
source "$HOME/.cargo/env"

# Verify installation
rustc --version
cargo --version
```

**Expected output:**
```
rustc 1.90.0 or later
cargo 1.90.0 or later
```

**Platform-specific notes:**

<details>
<summary><b>macOS Rust Installation</b></summary>

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add to shell profile (if not already done)
echo 'source "$HOME/.cargo/env"' >> ~/.zshrc
source ~/.zshrc

# Verify
rustc --version
```

**Apple Silicon Notes:**
- Rust automatically detects architecture (aarch64-apple-darwin)
- No additional configuration needed

**Intel Mac Notes:**
- Uses x86_64-apple-darwin target
- No additional configuration needed

</details>

<details>
<summary><b>Linux Rust Installation</b></summary>

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Source environment
source "$HOME/.cargo/env"

# Add to shell profile for persistence
echo 'source "$HOME/.cargo/env"' >> ~/.bashrc
# OR for zsh:
echo 'source "$HOME/.cargo/env"' >> ~/.zshrc

# Verify
rustc --version
cargo --version
```

</details>

<details>
<summary><b>Windows Rust Installation</b></summary>

**Prerequisites:**
- Install Visual Studio Build Tools FIRST (see [Windows Dependencies](#windows-dependencies))

```powershell
# Download and run rustup-init.exe
# From: https://rustup.rs/

# OR via PowerShell:
Invoke-WebRequest -Uri "https://win.rustup.rs/" -OutFile "rustup-init.exe"
.\rustup-init.exe -y

# Restart terminal

# Verify
rustc --version
cargo --version
```

**Common Issue:**
If you get "linker not found" errors, ensure Visual Studio Build Tools are installed.

</details>

#### Step 2: Install Bun

Bun is a fast JavaScript runtime and package manager used for the frontend build.

**macOS and Linux:**

```bash
# Install Bun
curl -fsSL https://bun.sh/install | bash

# Source environment (or restart terminal)
exec $SHELL

# Verify
bun --version
```

**Expected output:** `1.3.0` or later

**Windows:**

```powershell
# Install via PowerShell
powershell -c "irm bun.sh/install.ps1 | iex"

# Restart terminal

# Verify
bun --version
```

**Alternative (all platforms):**

```bash
# Install via npm (if Node.js is installed)
npm install -g bun
```

#### Step 3: Clone the Repository

```bash
# Clone from GitHub
git clone https://github.com/getAsterisk/opcode.git
cd opcode

# Verify you're in the right directory
ls -la
# Should see: src/, src-tauri/, package.json, README.md
```

#### Step 4: Install Frontend Dependencies

```bash
# Install JavaScript dependencies
bun install
```

**Expected output:**
```
bun install v1.3.0
+ 409 packages installed
```

**Build time:** ~5-10 seconds

**Common issues:**
- If `bun install` fails, ensure you have internet connectivity
- Try clearing cache: `rm -rf node_modules && bun install`

#### Step 5: Build the Frontend

```bash
# Build the React frontend
bun run build
```

**Expected output:**
```
vite v6.0.3 building for production...
✓ built in 3.7s
```

**Output location:** `dist/` directory

**Verification:**
```bash
ls dist/
# Should see: index.html, assets/, etc.
```

#### Step 6: Build and Run Opcode

**Development Mode (with hot reload):**

```bash
# Run in development mode
bun run tauri dev
```

**First compilation:**
- Downloads ~600+ Rust crates
- Compiles 651+ build artifacts
- Takes 15-20 minutes on first build
- Subsequent builds: 1-2 seconds

**Production Build:**

```bash
# Build optimized production binary
bun run tauri build
```

**Build time:** 5-10 minutes (first time), 2-3 minutes (subsequent)

**Output locations:**

<details>
<summary><b>macOS Build Artifacts</b></summary>

```
src-tauri/target/release/
├── opcode                              # Executable
└── bundle/
    ├── macos/opcode.app               # Application bundle
    └── dmg/opcode.dmg                 # DMG installer
```

**Installation:**
```bash
# Copy to Applications
cp -r src-tauri/target/release/bundle/macos/opcode.app /Applications/

# Or open DMG
open src-tauri/target/release/bundle/dmg/opcode.dmg
```

</details>

<details>
<summary><b>Linux Build Artifacts</b></summary>

```
src-tauri/target/release/
├── opcode                              # Executable
└── bundle/
    ├── appimage/opcode.AppImage       # AppImage
    ├── deb/opcode_*.deb               # Debian package
    └── rpm/opcode_*.rpm               # RPM package
```

**Installation:**
```bash
# AppImage
chmod +x src-tauri/target/release/bundle/appimage/opcode.AppImage
./src-tauri/target/release/bundle/appimage/opcode.AppImage

# Debian/Ubuntu
sudo dpkg -i src-tauri/target/release/bundle/deb/opcode_*.deb

# Fedora/RHEL
sudo rpm -i src-tauri/target/release/bundle/rpm/opcode_*.rpm
```

</details>

<details>
<summary><b>Windows Build Artifacts</b></summary>

```
src-tauri\target\release\
├── opcode.exe                         # Executable
└── bundle\
    ├── msi\opcode_*.msi              # MSI installer
    └── nsis\opcode_*_setup.exe       # NSIS installer
```

**Installation:**
```powershell
# Run executable directly
.\src-tauri\target\release\opcode.exe

# Or install via MSI
.\src-tauri\target\release\bundle\msi\opcode_*.msi
```

</details>

#### Alternative: Using Just

The project includes a `justfile` for common build tasks:

```bash
# Install Just (optional)
# macOS: brew install just
# Linux: cargo install just
# Windows: cargo install just

# Run development build
just dev

# Or quick build and run
just quick

# Run web server mode
just web

# Full rebuild from scratch
just rebuild

# Format Rust code
just fmt

# Run tests
just test
```

---

### Method 3: NixOS Installation

For NixOS users, a complete development environment is provided via `shell.nix`.

#### Using Nix Shell

```bash
# Clone repository
git clone https://github.com/getAsterisk/opcode.git
cd opcode

# Enter Nix development environment
nix-shell

# Build and run
just dev

# Or manually
bun install
bun run build
cd src-tauri && cargo run
```

#### What's Included in shell.nix

The Nix environment provides:
- Just (build automation)
- Git
- Bun and Node.js
- Rust toolchain (rustc, cargo, rustfmt, clippy)
- All Tauri dependencies (webkit2gtk, GTK3, etc.)
- Development utilities (curl, wget, jq)

#### Nix Flake (Optional)

For reproducible builds, consider creating a `flake.nix`:

```nix
{
  description = "Opcode - GUI for Claude Code";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells.default = import ./shell.nix { inherit pkgs; };
      }
    );
}
```

Enable flakes:
```bash
# Add to ~/.config/nix/nix.conf
experimental-features = nix-command flakes

# Use flake
nix develop
```

---

## Platform-Specific Instructions

### macOS Installation

<details>
<summary><b>Complete macOS Installation Guide</b></summary>

#### macOS Intel (x86_64)

**System Requirements:**
- macOS 10.15 (Catalina) or later
- Intel Core i3 or better
- 4 GB RAM minimum

**Step-by-step:**

1. **Install Xcode Command Line Tools:**
   ```bash
   xcode-select --install
   ```

2. **Install Rust:**
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
   source "$HOME/.cargo/env"
   echo 'source "$HOME/.cargo/env"' >> ~/.zshrc
   ```

3. **Install Bun:**
   ```bash
   curl -fsSL https://bun.sh/install | bash
   exec $SHELL
   ```

4. **Install Claude Code CLI:**
   - Download from [https://claude.ai/code](https://claude.ai/code)
   - Install the PKG file
   - Verify: `claude --version`

5. **Clone and Build:**
   ```bash
   git clone https://github.com/getAsterisk/opcode.git
   cd opcode
   bun install
   bun run build
   source "$HOME/.cargo/env" && bun run tauri dev
   ```

#### macOS Apple Silicon (aarch64)

**System Requirements:**
- macOS 11.0 (Big Sur) or later
- Apple M1, M1 Pro, M1 Max, M2, M3, or newer
- 4 GB RAM minimum

**Installation is identical to Intel, with automatic architecture detection.**

**Notes:**
- Rust automatically uses `aarch64-apple-darwin` target
- Performance is excellent on Apple Silicon
- Native ARM64 compilation (no Rosetta required)

#### Universal Binary (Intel + Apple Silicon)

To build a universal binary that runs natively on both architectures:

```bash
# Add Intel target to Apple Silicon Mac
rustup target add x86_64-apple-darwin

# Build universal binary
bun run tauri build --target universal-apple-darwin
```

**Output:** `src-tauri/target/universal-apple-darwin/release/bundle/`

#### macOS-Specific Issues

**Issue: "opcode.app is damaged and can't be opened"**
- **Cause:** Gatekeeper security
- **Solution:**
  ```bash
  xattr -cr /Applications/opcode.app
  ```

**Issue: "Cannot verify developer"**
- **Solution:** Right-click → Open (first launch only)
- Or: System Preferences → Security & Privacy → "Open Anyway"

**Issue: Transparent window not working**
- **Cause:** macOS private APIs disabled
- **Check:** `tauri.conf.json` has `"macOSPrivateApi": true`
- This is already configured in opcode

**Issue: Command Line Tools not found**
- **Solution:**
  ```bash
  sudo xcode-select --reset
  xcode-select --install
  ```

</details>

---

### Linux Installation

<details>
<summary><b>Ubuntu / Debian Installation</b></summary>

#### Ubuntu 20.04 / 22.04 / 24.04

**Full Installation:**

```bash
# Update package list
sudo apt update

# Install system dependencies
sudo apt install -y \
  pkg-config \
  libwebkit2gtk-4.1-dev \
  libgtk-3-dev \
  libssl-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev \
  build-essential \
  curl \
  wget \
  file \
  libxdo-dev \
  libsoup-3.0-dev \
  libjavascriptcoregtk-4.1-dev \
  patchelf

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
echo 'source "$HOME/.cargo/env"' >> ~/.bashrc

# Install Bun
curl -fsSL https://bun.sh/install | bash
exec $SHELL

# Install Claude Code CLI
# Visit https://claude.ai/code and download the .deb package
sudo dpkg -i claude-code-*.deb

# Clone and build Opcode
git clone https://github.com/getAsterisk/opcode.git
cd opcode
bun install
bun run build
bun run tauri dev
```

**For Ubuntu 20.04:**

If `libwebkit2gtk-4.1-dev` is unavailable:
```bash
sudo apt install libwebkit2gtk-4.0-dev
```

#### Debian 11 / 12

Same instructions as Ubuntu above.

**Additional notes:**
- Debian Stable may have older package versions
- Consider using Debian Testing or Sid for latest packages
- Or compile webkit2gtk from source if needed

</details>

<details>
<summary><b>Fedora Installation</b></summary>

#### Fedora 35 / 36 / 37 / 38+

```bash
# Install system dependencies
sudo dnf install -y \
  pkg-config \
  webkit2gtk4.1-devel \
  gtk3-devel \
  openssl-devel \
  libappindicator-gtk3-devel \
  librsvg2-devel \
  libsoup3-devel \
  javascriptcoregtk4.1-devel \
  patchelf \
  curl \
  wget \
  file

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
echo 'source "$HOME/.cargo/env"' >> ~/.bashrc

# Install Bun
curl -fsSL https://bun.sh/install | bash
exec $SHELL

# Install Claude Code CLI
# Visit https://claude.ai/code and download the RPM package
sudo dnf install claude-code-*.rpm

# Clone and build Opcode
git clone https://github.com/getAsterisk/opcode.git
cd opcode
bun install
bun run build
bun run tauri dev
```

</details>

<details>
<summary><b>Arch Linux Installation</b></summary>

#### Arch Linux (Rolling Release)

```bash
# Install system dependencies
sudo pacman -S --needed \
  webkit2gtk-4.1 \
  gtk3 \
  openssl \
  libappindicator-gtk3 \
  librsvg \
  libsoup3 \
  base-devel \
  curl \
  wget \
  file \
  patchelf

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
echo 'source "$HOME/.cargo/env"' >> ~/.bashrc

# Install Bun (via AUR or direct)
# Option 1: Direct installation
curl -fsSL https://bun.sh/install | bash

# Option 2: AUR (using yay or paru)
yay -S bun-bin
# OR
paru -S bun-bin

# Source environment
exec $SHELL

# Install Claude Code CLI
# Visit https://claude.ai/code
# Or use AUR if available

# Clone and build Opcode
git clone https://github.com/getAsterisk/opcode.git
cd opcode
bun install
bun run build
bun run tauri dev
```

#### Arch Linux: AUR Package (Future)

Once opcode is on AUR:
```bash
yay -S opcode
# OR
paru -S opcode
```

</details>

<details>
<summary><b>Linux-Specific Issues</b></summary>

#### Issue: webkit2gtk not found

**Ubuntu/Debian:**
```bash
# Try 4.1 first
sudo apt install libwebkit2gtk-4.1-dev

# Fallback to 4.0
sudo apt install libwebkit2gtk-4.0-dev
```

**Fedora:**
```bash
sudo dnf install webkit2gtk4.1-devel
```

**Arch:**
```bash
sudo pacman -S webkit2gtk-4.1
```

#### Issue: AppImage won't run

```bash
# Make executable
chmod +x opcode.AppImage

# If FUSE is missing
sudo apt install fuse libfuse2

# Extract and run
./opcode.AppImage --appimage-extract
./squashfs-root/AppRun
```

#### Issue: Wayland-specific problems

```bash
# Force X11 mode
GDK_BACKEND=x11 ./opcode
```

#### Issue: Missing libayatana-appindicator

**Ubuntu/Debian:**
```bash
sudo apt install libayatana-appindicator3-dev
```

**Fallback (for older systems):**
```bash
sudo apt install libappindicator3-dev
```

</details>

---

### Windows Installation

<details>
<summary><b>Complete Windows Installation Guide</b></summary>

#### Windows 10 / Windows 11

**System Requirements:**
- Windows 10 version 1809 or later, or Windows 11
- 64-bit processor (x64)
- 4 GB RAM minimum
- 2 GB free disk space

#### Step 1: Install Visual Studio Build Tools

**Critical prerequisite for Rust compilation.**

1. **Download:**
   - Visit: [https://visualstudio.microsoft.com/visual-cpp-build-tools/](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - Download "Build Tools for Visual Studio 2022"

2. **Install:**
   - Run `vs_BuildTools.exe`
   - Select **"Desktop development with C++"** workload
   - Ensure these components are checked:
     - MSVC v143 - VS 2022 C++ x64/x86 build tools (Latest)
     - Windows 10 SDK or Windows 11 SDK (10.0.19041.0 or later)
     - C++ CMake tools for Windows
   - Click "Install"

3. **Verify:**
   ```powershell
   # Restart terminal, then check
   where cl
   # Should show: C:\Program Files\Microsoft Visual Studio\...\cl.exe
   ```

#### Step 2: Install WebView2 (Windows 10 only)

**Windows 11**: Pre-installed, skip this step.

**Windows 10**:
1. Download: [Edge WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/)
2. Run the installer
3. Verify:
   ```powershell
   Test-Path "C:\Program Files (x86)\Microsoft\EdgeWebView\Application"
   # Should return: True
   ```

#### Step 3: Install Rust

```powershell
# Download rustup-init.exe
Invoke-WebRequest -Uri "https://win.rustup.rs/" -OutFile "rustup-init.exe"

# Run installer
.\rustup-init.exe -y

# Restart terminal (IMPORTANT!)
# Then verify
rustc --version
cargo --version
```

**Expected output:**
```
rustc 1.90.0 or later (x86_64-pc-windows-msvc)
cargo 1.90.0 or later
```

#### Step 4: Install Bun

```powershell
# Install via PowerShell
powershell -c "irm bun.sh/install.ps1 | iex"

# Restart terminal
# Verify
bun --version
```

#### Step 5: Install Git

If not already installed:
1. Download: [https://git-scm.com/download/win](https://git-scm.com/download/win)
2. Run installer (default options are fine)
3. Restart terminal

#### Step 6: Install Claude Code CLI

1. Visit [https://claude.ai/code](https://claude.ai/code)
2. Download Windows installer
3. Run the installer
4. Verify:
   ```powershell
   claude --version
   ```

#### Step 7: Clone and Build Opcode

```powershell
# Clone repository
git clone https://github.com/getAsterisk/opcode.git
cd opcode

# Install frontend dependencies
bun install

# Build frontend
bun run build

# Build and run Opcode
bun run tauri dev
```

**First build time**: 15-20 minutes

**Production build:**
```powershell
bun run tauri build
```

**Output location:**
```
src-tauri\target\release\opcode.exe
src-tauri\target\release\bundle\msi\opcode_*.msi
```

#### Windows-Specific Issues

**Issue: "MSVC not found" or "link.exe not found"**
- **Cause:** Visual Studio Build Tools not installed or not in PATH
- **Solution:**
  1. Ensure Build Tools are installed
  2. Restart terminal
  3. Check: `where cl` should show the compiler path
  4. If still fails, run:
     ```powershell
     # Find Visual Studio path
     & "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath

     # Run Developer Command Prompt
     # (substitute with your VS path)
     & "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat"
     ```

**Issue: "WebView2 not found"**
- **Windows 10:** Install WebView2 Runtime (see Step 2)
- **Windows 11:** Should be pre-installed
- **Verify:**
  ```powershell
  Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" -ErrorAction SilentlyContinue
  ```

**Issue: Build fails with "out of memory"**
- **Solution:**
  ```powershell
  # Build with fewer parallel jobs
  cd src-tauri
  cargo build -j 2
  ```

**Issue: Bun command not found after installation**
- **Solution:**
  1. Restart terminal (IMPORTANT)
  2. If still not found, manually add to PATH:
     ```powershell
     $env:Path += ";$env:USERPROFILE\.bun\bin"
     ```
  3. Or add permanently via System Properties → Environment Variables

**Issue: Antivirus blocks compilation**
- **Solution:** Add exclusions for:
  - `opcode/src-tauri/target/` directory
  - `C:\Users\<YourUser>\.cargo\` directory
  - `rustc.exe` and `cargo.exe`

</details>

---

## Post-Installation

### Initial Setup

After installation, complete these setup steps:

#### 1. Verify Claude Code CLI

```bash
# Check Claude Code is installed
claude --version

# Check authentication
claude auth status

# If not authenticated
claude auth login
```

#### 2. Configure Claude Data Directory

Opcode reads from `~/.claude/projects/` directory:

```bash
# Verify directory exists
ls ~/.claude/projects/

# If it doesn't exist, create it
mkdir -p ~/.claude/projects/

# Run Claude Code once to initialize
claude
```

#### 3. First Launch

**macOS:**
```bash
open /Applications/opcode.app
# OR
/Applications/opcode.app/Contents/MacOS/opcode
```

**Linux:**
```bash
opcode
# OR
./opcode.AppImage
```

**Windows:**
```powershell
Start-Process "C:\Program Files\opcode\opcode.exe"
# OR
opcode
```

#### 4. Grant Permissions

**macOS:**
- Allow access to ~/.claude directory when prompted
- Grant any accessibility permissions if requested

**Linux:**
- May need to allow filesystem access depending on sandbox settings
- AppImage: Usually has full access
- Flatpak/Snap (future): Grant home directory access

**Windows:**
- Allow Windows Defender firewall access if prompted
- Grant file system permissions

#### 5. Configuration Files

Opcode stores configuration in:
```
~/.config/opcode/           # Linux/macOS
%APPDATA%\opcode\           # Windows
```

**Contents:**
- `settings.json` - User preferences
- `agents.json` - Custom agents
- `mcp-servers.json` - MCP server configurations
- `checkpoints.db` - SQLite database for timeline

### Environment Variables

Optional environment variables for customization:

```bash
# Custom Claude data directory
export CLAUDE_HOME="$HOME/.claude"

# Custom opcode config directory
export OPCODE_CONFIG="$HOME/.config/opcode"

# Log level (error, warn, info, debug, trace)
export RUST_LOG=opcode=info

# Disable telemetry (opcode doesn't have telemetry, but for clarity)
export OPCODE_TELEMETRY=false
```

**Add to shell profile:**

```bash
# macOS/Linux: ~/.zshrc or ~/.bashrc
echo 'export RUST_LOG=opcode=info' >> ~/.zshrc

# Windows: System Properties → Environment Variables
```

### Shell Integration

**Add to PATH (if not installed via package manager):**

```bash
# macOS/Linux
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.zshrc

# Windows (PowerShell profile)
Add-Content $PROFILE 'PATH="$env:PATH;C:\Users\<YourUser>\.local\bin"'
```

### File Associations (Future)

Associate `.claude` project files with opcode:

**macOS:**
```bash
# Set opcode as default handler
# (This will be automated in future releases)
```

**Linux:**
```bash
# Create MIME type association
xdg-mime default opcode.desktop application/x-claude-project
```

**Windows:**
```powershell
# Associate .claude files
# (This will be automated in the installer)
```

---

## Verification

### Verify Installation

After installation, verify everything is working:

#### 1. Check Application Launch

```bash
# Launch opcode
opcode --version
# Expected: opcode 0.2.1 or later

# OR launch GUI
opcode
```

#### 2. Verify Dependencies

```bash
# Claude Code CLI
claude --version
# Expected: claude version 1.x.x

# Rust (for development)
rustc --version
# Expected: rustc 1.90.0 or later

# Bun (for development)
bun --version
# Expected: 1.3.0 or later
```

#### 3. Check Data Directory

```bash
# Verify Claude data directory exists
ls ~/.claude/projects/

# Expected: Directory exists with your Claude Code projects
```

#### 4. Test Basic Functionality

1. **Launch opcode**
2. **Check Projects tab**: Should list projects from `~/.claude/projects/`
3. **Check CC Agents tab**: Should show agent creation interface
4. **Create a test agent**: Verify agent creation works
5. **Run a simple Claude Code command**: Test integration

#### 5. Check Build Artifacts (for developers)

```bash
# Verify build succeeded
ls src-tauri/target/release/

# Expected files:
# - opcode (executable)
# - opcode-web (web server binary)
```

### Smoke Test

Quick smoke test to verify core functionality:

```bash
# 1. Launch opcode in headless mode (future feature)
# opcode --headless

# 2. Check CLI integration
echo "Test" | opcode --stdin

# 3. Check web server mode
cd src-tauri
cargo run --bin opcode-web -- --port 8080 &
# Visit http://localhost:8080
# Stop: kill %1
```

### Health Check Script

Create a health check script:

```bash
#!/bin/bash
# save as: ~/bin/opcode-health-check.sh

echo "=== Opcode Health Check ==="

# Check opcode
if command -v opcode &> /dev/null; then
  echo "✓ opcode installed"
  opcode --version
else
  echo "✗ opcode not found"
fi

# Check Claude Code CLI
if command -v claude &> /dev/null; then
  echo "✓ Claude Code CLI installed"
  claude --version
else
  echo "✗ Claude Code CLI not found"
fi

# Check data directory
if [ -d "$HOME/.claude/projects" ]; then
  echo "✓ Claude data directory exists"
  echo "  Projects: $(ls -1 ~/.claude/projects | wc -l)"
else
  echo "✗ Claude data directory missing"
fi

# Check Rust (for dev)
if command -v rustc &> /dev/null; then
  echo "✓ Rust installed (dev)"
  rustc --version
else
  echo "⚠ Rust not installed (required for development only)"
fi

# Check Bun (for dev)
if command -v bun &> /dev/null; then
  echo "✓ Bun installed (dev)"
  bun --version
else
  echo "⚠ Bun not installed (required for development only)"
fi

echo ""
echo "=== Health Check Complete ==="
```

Run the health check:
```bash
chmod +x ~/bin/opcode-health-check.sh
~/bin/opcode-health-check.sh
```

---

## Troubleshooting

### Common Installation Issues

<details>
<summary><b>Issue: Command not found</b></summary>

**Symptoms:**
```bash
opcode
# bash: opcode: command not found
```

**Solutions:**

1. **Check installation location:**
   ```bash
   # macOS/Linux
   which opcode
   find /Applications -name "opcode.app" 2>/dev/null
   find ~/.local -name "opcode" 2>/dev/null

   # Windows
   where opcode
   ```

2. **Add to PATH:**
   ```bash
   # macOS/Linux
   export PATH="$PATH:/path/to/opcode/directory"

   # Windows
   $env:Path += ";C:\path\to\opcode\directory"
   ```

3. **Run with full path:**
   ```bash
   # macOS
   /Applications/opcode.app/Contents/MacOS/opcode

   # Linux
   ~/.local/bin/opcode

   # Windows
   "C:\Program Files\opcode\opcode.exe"
   ```

</details>

<details>
<summary><b>Issue: Build fails with dependency errors</b></summary>

**Linux (webkit2gtk missing):**
```bash
# Ubuntu/Debian
sudo apt install libwebkit2gtk-4.1-dev

# Fedora
sudo dnf install webkit2gtk4.1-devel

# Arch
sudo pacman -S webkit2gtk-4.1
```

**macOS (Xcode tools missing):**
```bash
xcode-select --install
sudo xcode-select --reset
```

**Windows (MSVC missing):**
- Install Visual Studio Build Tools
- Select "Desktop development with C++"
- Restart terminal after installation

</details>

<details>
<summary><b>Issue: Rust compilation errors</b></summary>

**Error: "linker not found"**

**Linux:**
```bash
sudo apt install build-essential
```

**macOS:**
```bash
xcode-select --install
```

**Windows:**
- Install Visual Studio Build Tools
- Restart terminal

**Error: "out of memory during compilation"**

```bash
# Build with fewer parallel jobs
cd src-tauri
cargo build -j 2
```

**Error: "failed to fetch"**

```bash
# Update Rust and retry
rustup update
cd src-tauri
rm -rf target/
cargo clean
cargo build
```

</details>

<details>
<summary><b>Issue: Frontend build fails</b></summary>

**Error: "bun not found"**

```bash
# Reinstall Bun
curl -fsSL https://bun.sh/install | bash
exec $SHELL
```

**Error: "node-gyp errors"**

Bun should handle this, but if using npm:
```bash
# Linux
sudo apt install python3 make g++

# macOS
xcode-select --install

# Windows
npm install --global windows-build-tools
```

**Error: "out of memory"**

```bash
# Increase Node/Bun memory
export NODE_OPTIONS="--max-old-space-size=4096"
bun run build
```

**Error: "vite build failed"**

```bash
# Clear cache and rebuild
rm -rf node_modules dist
bun install
bun run build
```

</details>

<details>
<summary><b>Issue: Claude Code CLI not found</b></summary>

**Verify installation:**
```bash
# Check if installed
claude --version

# Check PATH
echo $PATH | grep -i claude

# Find Claude Code binary
# macOS
find /Applications -name "claude" 2>/dev/null
find /usr/local -name "claude" 2>/dev/null

# Linux
which claude
find /opt -name "claude" 2>/dev/null

# Windows
where claude
Get-Command claude
```

**Reinstall Claude Code:**
1. Visit [https://claude.ai/code](https://claude.ai/code)
2. Download installer for your platform
3. Install
4. Verify: `claude --version`

**Add to PATH manually:**
```bash
# macOS/Linux
export PATH="$PATH:/path/to/claude"
echo 'export PATH="$PATH:/path/to/claude"' >> ~/.zshrc

# Windows
$env:Path += ";C:\path\to\claude"
```

</details>

<details>
<summary><b>Issue: Permission denied errors</b></summary>

**macOS:**
```bash
# Grant full disk access
# System Preferences → Security & Privacy → Privacy → Full Disk Access
# Add opcode.app

# Fix file permissions
chmod +x /Applications/opcode.app/Contents/MacOS/opcode
```

**Linux:**
```bash
# Make executable
chmod +x opcode
chmod +x opcode.AppImage

# Fix directory permissions
chmod 755 ~/.claude
chmod 755 ~/.config/opcode
```

**Windows:**
```powershell
# Run as administrator
Start-Process "opcode.exe" -Verb RunAs

# Fix permissions
icacls "C:\Program Files\opcode" /grant Users:F /T
```

</details>

<details>
<summary><b>Issue: Application won't start</b></summary>

**Check logs:**

```bash
# macOS
tail -f ~/Library/Logs/opcode/opcode.log

# Linux
journalctl --user -xe | grep opcode
tail -f ~/.local/share/opcode/logs/opcode.log

# Windows
Get-Content "$env:APPDATA\opcode\logs\opcode.log" -Tail 50
```

**Run in debug mode:**

```bash
# macOS/Linux
RUST_LOG=debug opcode

# Windows
$env:RUST_LOG="debug"
opcode
```

**Common causes:**

1. **Missing dependencies:**
   - Verify all dependencies installed (see platform-specific sections)

2. **Conflicting versions:**
   ```bash
   # Clean and rebuild
   cd opcode
   rm -rf node_modules dist src-tauri/target
   bun install
   bun run build
   bun run tauri build
   ```

3. **Corrupted config:**
   ```bash
   # Reset configuration
   mv ~/.config/opcode ~/.config/opcode.backup
   opcode
   ```

</details>

<details>
<summary><b>Issue: Slow build times</b></summary>

**First build is always slow (15-20 minutes)**
- This is normal
- Rust compiles 650+ crates on first build

**Subsequent builds slow (more than 2-3 minutes):**

**Enable incremental compilation:**
```bash
# Add to ~/.cargo/config.toml
mkdir -p ~/.cargo
cat >> ~/.cargo/config.toml <<EOF
[build]
incremental = true
EOF
```

**Use release-opt profile:**
```toml
# Add to src-tauri/Cargo.toml
[profile.release-opt]
inherits = "release"
opt-level = 2  # Faster compile, slightly slower runtime
```

**Use mold linker (Linux only):**
```bash
# Install mold
sudo apt install mold  # Ubuntu
sudo dnf install mold  # Fedora

# Configure Cargo
cat >> ~/.cargo/config.toml <<EOF
[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=mold"]
EOF
```

**Use lld linker (macOS/Windows):**
```bash
# Install lld
# macOS: brew install llvm
# Windows: Included with Visual Studio

# Configure Cargo
cat >> ~/.cargo/config.toml <<EOF
[target.x86_64-apple-darwin]
rustflags = ["-C", "link-arg=-fuse-ld=lld"]

[target.x86_64-pc-windows-msvc]
rustflags = ["-C", "link-arg=/usr/bin/lld-link"]
EOF
```

**Use sccache for caching:**
```bash
# Install sccache
cargo install sccache

# Configure
export RUSTC_WRAPPER=sccache
echo 'export RUSTC_WRAPPER=sccache' >> ~/.zshrc
```

</details>

### Platform-Specific Troubleshooting

See the platform-specific installation sections above for detailed troubleshooting.

### Getting Help

If you're still stuck:

1. **Check existing issues:** [GitHub Issues](https://github.com/getAsterisk/opcode/issues)
2. **Search documentation:** See `docs/` directory
3. **Join Discord:** [Discord Invite](https://discord.com/invite/KYwhHVzUsY)
4. **Create an issue:** [New Issue](https://github.com/getAsterisk/opcode/issues/new)

**When reporting issues, include:**
- Operating system and version
- Rust version (`rustc --version`)
- Bun version (`bun --version`)
- Claude Code CLI version (`claude --version`)
- Error message or log output
- Steps to reproduce

---

## Upgrading

### Upgrading Opcode

#### From Pre-built Releases

**macOS:**
```bash
# Download latest DMG
curl -LO https://github.com/getAsterisk/opcode/releases/latest/download/opcode_macos_universal.dmg

# Replace existing app
rm -rf /Applications/opcode.app
open opcode_macos_universal.dmg
# Drag to Applications
```

**Linux (AppImage):**
```bash
# Download latest AppImage
curl -LO https://github.com/getAsterisk/opcode/releases/latest/download/opcode_linux_x86_64.AppImage

# Replace existing binary
chmod +x opcode_linux_x86_64.AppImage
mv opcode_linux_x86_64.AppImage ~/.local/bin/opcode
```

**Linux (.deb):**
```bash
# Download latest .deb
curl -LO https://github.com/getAsterisk/opcode/releases/latest/download/opcode_linux_x86_64.deb

# Upgrade
sudo dpkg -i opcode_linux_x86_64.deb
```

#### From Source

```bash
# Navigate to repository
cd opcode

# Pull latest changes
git fetch --tags
git pull origin main

# Or checkout specific version
git fetch --tags
git checkout v0.2.1

# Clean build
rm -rf node_modules dist src-tauri/target
bun install
bun run build
bun run tauri build

# Install
# (Follow platform-specific installation steps)
```

### Upgrading Dependencies

#### Upgrade Rust

```bash
# Update Rust toolchain
rustup update

# Verify
rustc --version
```

#### Upgrade Bun

```bash
# Upgrade Bun
bun upgrade

# Verify
bun --version
```

#### Upgrade Claude Code CLI

Visit [https://claude.ai/code](https://claude.ai/code) and download the latest installer.

#### Upgrade Frontend Dependencies

```bash
cd opcode
bun update
bun install
```

#### Upgrade Rust Dependencies

```bash
cd opcode/src-tauri
cargo update
```

### Migration Notes

#### Migrating from 0.1.x to 0.2.x

**Breaking changes:**
- Configuration file format changed
- Database schema updated

**Migration steps:**

1. **Backup your data:**
   ```bash
   cp -r ~/.config/opcode ~/.config/opcode.backup
   ```

2. **Upgrade opcode:**
   ```bash
   # (Follow upgrade steps above)
   ```

3. **First launch:**
   - Opcode will automatically migrate your configuration
   - Review settings after migration

4. **If migration fails:**
   ```bash
   # Restore backup
   rm -rf ~/.config/opcode
   mv ~/.config/opcode.backup ~/.config/opcode

   # Report issue on GitHub
   ```

---

## Uninstallation

### Uninstall Opcode

#### macOS

```bash
# Remove application
rm -rf /Applications/opcode.app

# Remove configuration (optional)
rm -rf ~/.config/opcode

# Remove cache (optional)
rm -rf ~/Library/Caches/opcode
rm -rf ~/Library/Application\ Support/opcode
```

#### Linux

**AppImage:**
```bash
# Remove binary
rm ~/.local/bin/opcode

# Remove desktop entry
rm ~/.local/share/applications/opcode.desktop

# Remove configuration (optional)
rm -rf ~/.config/opcode

# Remove cache (optional)
rm -rf ~/.cache/opcode
```

**.deb:**
```bash
# Uninstall package
sudo apt remove opcode

# Remove configuration (optional)
rm -rf ~/.config/opcode
```

**Flatpak (future):**
```bash
flatpak uninstall opcode
```

#### Windows

**Via Settings:**
1. Settings → Apps → opcode → Uninstall

**Via PowerShell:**
```powershell
# Uninstall MSI
Get-Package -Name "opcode" | Uninstall-Package

# Remove configuration (optional)
Remove-Item -Recurse -Force "$env:APPDATA\opcode"
```

### Uninstall Dependencies

**Only uninstall these if you're not using them for other projects:**

#### Uninstall Rust

```bash
rustup self uninstall
```

#### Uninstall Bun

```bash
# macOS/Linux
rm -rf ~/.bun

# Windows
Remove-Item -Recurse -Force "$env:USERPROFILE\.bun"
```

#### Uninstall Claude Code CLI

**macOS:**
```bash
# Find installation
find /Applications -name "Claude Code.app"
find /usr/local -name "claude"

# Remove
rm -rf "/Applications/Claude Code.app"
sudo rm /usr/local/bin/claude
```

**Linux:**
```bash
# .deb
sudo apt remove claude-code

# Manual
sudo rm /usr/local/bin/claude
```

**Windows:**
```powershell
# Via Settings
Settings → Apps → Claude Code → Uninstall
```

### Clean Uninstall

To remove all traces:

```bash
# Remove application
# (Follow platform-specific steps above)

# Remove all configuration and data
rm -rf ~/.config/opcode
rm -rf ~/.local/share/opcode
rm -rf ~/.cache/opcode

# macOS: Remove additional data
rm -rf ~/Library/Application\ Support/opcode
rm -rf ~/Library/Caches/opcode
rm -rf ~/Library/Logs/opcode

# Windows: Remove additional data
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\opcode"
Remove-Item -Recurse -Force "$env:APPDATA\opcode"
```

---

## Installation History (Original)

This section preserves the original installation history from the macOS Apple Silicon environment where opcode was first built.

### System Environment
- **OS**: macOS (Darwin 24.4.0)
- **Architecture**: Apple Silicon (aarch64-apple-darwin)
- **Date**: October 2025

### Installation Steps Executed

#### 1. Installed Bun
```bash
curl -fsSL https://bun.sh/install | bash
# Installed to: ~/.bun/bin/bun
# Version: 1.3.0
```

#### 2. Installed Rust
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
# Installed: rustc 1.90.0
# Toolchain: stable-aarch64-apple-darwin
```

#### 3. Installed Dependencies
```bash
bun install
# Installed 409 packages in 9.07s
```

#### 4. Built Frontend
```bash
bun run build
# Generated dist/ folder with React app
# Build time: ~3.7s
```

#### 5. First Rust Compilation
```bash
bun run tauri dev
# First compile: ~19 seconds
# Downloaded 600+ crates
# Generated 651 build artifacts
```

### Build Times (Original Environment)

- **First compile**: ~19 seconds (downloads all crates)
- **Subsequent compiles**: ~1-2 seconds (cached)
- **Frontend build**: ~3-4 seconds
- **Full production build**: ~5-7 minutes

### Compilation Notes

#### Warnings (Non-Critical)
The codebase had some Rust warnings:
- `non_snake_case` warnings in `web_server.rs:236` and `:244`
- `dead_code` warning for unused `register_sidecar_process` method

These don't affect functionality but could be cleaned up.

---

## Additional Resources

### Documentation

- **Main README**: `/Users/max/local/opcode/README.md`
- **Development Guide**: `/Users/max/local/opcode/CLAUDE.md`
- **Quick Start**: `/Users/max/local/opcode/docs/quick-start.md`
- **Troubleshooting**: `/Users/max/local/opcode/docs/troubleshooting.md`
- **Web Server Notes**: `/Users/max/local/opcode/web_server.design.md`

### External Links

- **Opcode GitHub**: [https://github.com/getAsterisk/opcode](https://github.com/getAsterisk/opcode)
- **Claude Code**: [https://claude.ai/code](https://claude.ai/code)
- **Discord Community**: [https://discord.com/invite/KYwhHVzUsY](https://discord.com/invite/KYwhHVzUsY)
- **Tauri Documentation**: [https://tauri.app/](https://tauri.app/)
- **Rust Documentation**: [https://www.rust-lang.org/](https://www.rust-lang.org/)
- **Bun Documentation**: [https://bun.sh/](https://bun.sh/)

### Version Information

- **Current Version**: 0.2.1
- **Minimum Rust**: 1.70.0
- **Minimum Bun**: 1.0.0
- **Tauri Version**: 2.0
- **React Version**: 18.3.1

---

## Frequently Asked Questions

### General Questions

**Q: Is opcode free and open source?**
A: Yes, opcode is licensed under AGPL-3.0.

**Q: Does opcode work without Claude Code CLI?**
A: No, Claude Code CLI is required. Opcode is a GUI wrapper for Claude Code.

**Q: Does opcode send telemetry?**
A: No, opcode does not collect or send any telemetry data.

**Q: Can I use opcode for commercial projects?**
A: Yes, but review the AGPL-3.0 license terms.

### Installation Questions

**Q: Why is the first build so slow?**
A: Rust compiles 650+ dependencies on first build. This is normal. Subsequent builds are fast (1-2 seconds).

**Q: Can I install opcode without building from source?**
A: Pre-built binaries will be available soon. For now, building from source is required.

**Q: Do I need to install Node.js?**
A: No, Bun is used instead of Node.js.

**Q: Can I use npm/yarn instead of Bun?**
A: Technically yes, but Bun is recommended and tested.

### Platform Questions

**Q: Does opcode work on macOS Catalina (10.15)?**
A: Yes, minimum version is macOS 10.15.

**Q: Does opcode work on Apple Silicon?**
A: Yes, natively. A universal binary is also available for Intel Macs.

**Q: Does opcode work on Ubuntu 18.04?**
A: No, minimum is Ubuntu 20.04 due to webkit2gtk requirements.

**Q: Does opcode work on Windows 7?**
A: No, minimum is Windows 10 version 1809.

### Feature Questions

**Q: Can I run opcode as a web server?**
A: Yes, use `cargo run --bin opcode-web` for web server mode. **Warning**: This is not production-ready (single user/session only).

**Q: Does opcode support Docker?**
A: Not officially, but you can containerize it. A Dockerfile is not provided.

**Q: Can I contribute to opcode?**
A: Yes! See CONTRIBUTING.md for guidelines.

---

## Conclusion

You now have a complete guide to installing opcode on any platform. For quick reference:

1. **Install prerequisites**: Rust, Bun, Claude Code CLI
2. **Clone repository**: `git clone https://github.com/getAsterisk/opcode.git`
3. **Build frontend**: `bun install && bun run build`
4. **Build and run**: `bun run tauri dev` or `bun run tauri build`

For issues, consult the [Troubleshooting](#troubleshooting) section or reach out on [Discord](https://discord.com/invite/KYwhHVzUsY).

**Happy coding with opcode!**
