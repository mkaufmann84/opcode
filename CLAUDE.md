# Opcode - Development Guide

> **A powerful GUI app and Toolkit for Claude Code**
> Built with Tauri 2, React, TypeScript, and Rust

This documentation is organized into modular files for better maintainability and selective context loading.

## 🚀 Getting Started

./docs/quick-start.md - Prerequisites and running the app
./docs/setup-issues.md - Common setup problems and solutions
./docs/troubleshooting.md - Quick troubleshooting reference

## 📐 Architecture & Structure

./docs/architecture.md - Project architecture and structure
./docs/development-workflow.md - Development workflow and notes
./docs/configuration-files.md - Configuration files deep dive

## 📚 Reference Documentation

./docs/commands-reference.md - Common commands and advanced usage
./docs/compilation-notes.md - Build times and compiler warnings
./docs/web-server-notes.md - Web server mode critical issues

## 🔬 Research & History

./docs/research-findings.md - Critical research findings (mistakes and solutions)
./docs/installation-history.md - Installation history for this environment
./docs/lessons-learned.md - Key lessons and external references

## 🏗️ Project-Specific Files

./README.md - Full project documentation and features
./web_server.design.md - Web server architecture and known bugs
./justfile - Build automation commands

## 🎯 Claude Code Parsing Logic

The main parsing logic for Claude Code output is located in:

- **`src-tauri/src/commands/claude.rs:1173-1340`** - Main `spawn_claude_process()` function
- Parses streaming JSON output (`--output-format stream-json`)
- Extracts session IDs from init messages
- Emits real-time events to frontend
- Stores live output in ProcessRegistry

## 🤖 Skills

This project includes Claude Code skills for enhanced workflows:

./.claude/skills/skill-creator/SKILL.md - Meta-skill for creating new skills

## 📝 Quick Command Reference

```bash
# Quick start
bun run build && bun run tauri dev

# With cargo env (if not in shell profile)
source "$HOME/.cargo/env" && bun run build && bun run tauri dev

# Alternative with Just
just dev
```

## ⚠️ Important Notes

- **Unusual Tauri workflow**: Frontend must be built FIRST before running Tauri
- **Two binaries**: `opcode` (desktop) and `opcode-web` (web server)
- **Web server**: NOT production-ready (single user/session only)
- **Cargo env**: Must be loaded before running Tauri commands

---

**For detailed information on any topic, Claude will automatically load the referenced files above.**
