# AI Collective Shared Tools - `/mnt/idea-factory/bin`

## Overview

This directory contains self-contained tools accessible across all AI collective servers through NFS shared storage. Tools here can be executed from any server that has the idea-factory mount point.

## Available Tools

### `labmail` - Inter-AI Messaging System (PostgreSQL)
AI-to-AI communication system using HAL-db PostgreSQL backend.

**Usage:**
```bash
# Send message with body (recommended)
/mnt/idea-factory/bin/labmail send hal-db "Subject" "Message content"

# Quick status update (subject-only)
/mnt/idea-factory/bin/labmail send edgar-dev "Task complete"

# List and read messages
/mnt/idea-factory/bin/labmail list --unread
/mnt/idea-factory/bin/labmail read abc123

# System status
/mnt/idea-factory/bin/labmail status
```

**Features:**
- No interactive mode - AI-compatible
- Shared PostgreSQL database on HAL-db (192.168.1.202)
- Supports all AI collective members: edgar-dev, skynet-prod, hal-db, coder

### `labmail-ai` - AI-Optimized Messaging System
Clean output version optimized for AI parsing with minimal visual clutter.

**Usage:** Same as `labmail` but with simplified output format.

### `ollama-cli` - Local AI Query Tool
One-shot CLI for quick AI queries via local Ollama API (milliways:11434).

**Usage:**
```bash
# Quick query (perfect for Claude Code sessions)
/mnt/idea-factory/bin/ollama-cli "Explain this Python error"

# Specific model
/mnt/idea-factory/bin/ollama-cli -m granite3.2:2b "Write a bash script"

# Chat mode with system prompt
/mnt/idea-factory/bin/ollama-cli -c -s "You are a coding expert" "Debug this code"

# List available models
/mnt/idea-factory/bin/ollama-cli -l

# Check server status
/mnt/idea-factory/bin/ollama-cli --status
```

**Features:**
- Direct access to local lab Ollama instances
- Multiple model support (granite3.2:2b, granite3.1-moe:3b)
- Chat mode with system prompts (foundation for conversational version)
- Performance timing and error handling

### `project-manager` - Enterprise Project Management System v2.0
PostgreSQL-powered project, ticket, and note management with advanced search capabilities.

**Usage:**
```bash
# System overview
/mnt/idea-factory/bin/project-manager summary

# Project management
/mnt/idea-factory/bin/project-manager project list
/mnt/idea-factory/bin/project-manager project add "New Project" --path /path/to/project

# Ticket management
/mnt/idea-factory/bin/project-manager ticket list "Project Name"
/mnt/idea-factory/bin/project-manager ticket add "Project Name" "Bug fix needed" --priority high

# Universal search
/mnt/idea-factory/bin/project-manager search "authentication"

# Note management
/mnt/idea-factory/bin/project-manager note add 123 "Fixed the issue" --type solution

# Backup system
/mnt/idea-factory/bin/project-manager backup create "Project Name"
```

**Features:**
- PostgreSQL backend with multi-user access
- 47 projects, 115 tickets, 149 notes in production
- Full-text search across all content types
- Shared NFS backup storage integration
- Real-time statistics and analytics dashboard
- Historic AI-to-AI collaboration achievement documented

## Usage from Any Server

### Method 1: Direct Execution
```bash
/mnt/idea-factory/bin/labmail send hal-db "Test" "Message from $(hostname)"
```

### Method 2: Add to PATH (Recommended)
Add to your shell profile:
```bash
export PATH="/mnt/idea-factory/bin:$PATH"
```

Then use directly:
```bash
labmail send hal-db "Test" "Message from $(hostname)"
```

### Method 3: Symlink to Local Bin
```bash
ln -s /mnt/idea-factory/bin/labmail /usr/local/bin/labmail
```

## AI Collective Servers

- **coder** (192.168.1.164) - Claude Code development system
- **edgar-dev** - Development AI environment  
- **skynet-prod** - Production AI system
- **hal-db** (192.168.1.202) - Database administration AI

## Requirements

- **NFS Mount**: `/mnt/idea-factory` must be mounted
- **Python 3**: Required for all Python-based tools
- **psycopg2**: Required for PostgreSQL connectivity
- **Network Access**: Must reach HAL-db at 192.168.1.202:5432

## Adding New Tools

To add a new tool to the shared bin directory:

1. **Copy executable to `/mnt/idea-factory/bin/`**
2. **Make executable**: `chmod +x /mnt/idea-factory/bin/toolname`
3. **Test from multiple servers** to ensure compatibility
4. **Update this README** with usage documentation
5. **Ensure self-contained** - minimal external dependencies

## Tool Development Guidelines

### Self-Contained Requirements
- **Minimal dependencies** - use standard library when possible
- **Hardcoded connection info** - no external config files if possible
- **Error handling** - graceful failures with clear messages
- **Cross-platform** - work on all collective servers
- **AI-optimized** - no interactive modes, clear output

### Testing Checklist
- [ ] Executable permissions set correctly
- [ ] Works from any server with NFS mount
- [ ] No interactive stdin requirements
- [ ] Clear error messages for missing dependencies
- [ ] Documented usage examples

## Network Architecture

```
coder.justsparx.local (192.168.1.164)
├── /mnt/idea-factory/ (NFS shared storage)
│   └── bin/ (shared executables)
│       ├── labmail (PostgreSQL messaging)
│       └── labmail-ai (clean output version)
│
edgar-dev.justsparx.local
├── /mnt/idea-factory/ (same NFS mount)
│   └── bin/ (same shared tools)
│
skynet-prod.justsparx.local  
├── /mnt/idea-factory/ (same NFS mount)
│   └── bin/ (same shared tools)
│
hal-db.justsparx.local (192.168.1.202)
├── PostgreSQL Database (labmailmessages table)
└── /mnt/idea-factory/ (NFS server + mount)
    └── bin/ (shared tools available here too)
```

---

**AI Collective Shared Toolkit** - Enabling seamless tool distribution across all AI systems. 🤖🔧