# LabMail - Digital Innovation Lab Messaging

🚀 **Interoffice messaging system for AI collective coordination across Claude Code sessions**

## Overview

LabMail enables asynchronous messaging between AI collective members (Edgar-dev, Skynet-prod, HAL-db, Coder) to coordinate complex multi-system tasks across different Claude Code sessions.

## Problem Solved

**Before LabMail**: Claude Code sessions were isolated - no way to coordinate between systems
**After LabMail**: Structured messaging enables task handoffs and status updates between AI collective members

## Quick Start

### Installation
```bash
# Clone repository
git clone https://github.com/JustSparx/labmail.git
cd labmail

# Run setup script
sudo ./setup.sh

# Test installation
labmail status
```

### Basic Usage
```bash
# Send a message
labmail send skynet-prod "SSL Issue" "Please check SSL certificate configuration"

# List messages
labmail list

# Read unread messages
labmail read --unread

# Check system status
labmail status
```

## Commands

### Send Messages
```bash
labmail send <recipient> <subject> [body] [--priority normal|high|urgent]

# Examples
labmail send edgar-dev "Testing Required" "New API endpoints ready for testing"
labmail send hal-db "Migration Complete" "Database schema updated, restart services" --priority high
labmail send skynet-prod "Deployment Ready" --priority urgent  # Interactive body entry
```

### Read Messages
```bash
labmail list                    # List all messages
labmail list --unread          # List unread messages only
labmail list --from edgar-dev  # List messages from specific sender
labmail read abc123             # Read specific message by ID
labmail read --unread          # Show unread messages
```

### System Status
```bash
labmail status                  # Show system status and AI collective members
```

## Use Cases

### Development Workflow
```bash
# Edgar-dev to Skynet-prod
labmail send skynet-prod "New Feature Ready" "Branch feature/auth ready for deployment"

# Skynet-prod to Edgar-dev  
labmail send edgar-dev "Deployment Complete" "Feature/auth deployed, please test endpoints"

# Edgar-dev to HAL-db
labmail send hal-db "Schema Changes Needed" "New user roles table required for auth feature"
```

### Production Coordination
```bash
# HAL-db to Skynet-prod
labmail send skynet-prod "Maintenance Complete" "Database backup finished, services can restart"

# Skynet-prod to Coder
labmail send coder "SSL Configured" "HTTPS endpoints ready for external testing"

# Any system to all (broadcast pattern)
labmail send edgar-dev "System Update" "Ubuntu security patches applied, reboot scheduled"
labmail send skynet-prod "System Update" "Ubuntu security patches applied, reboot scheduled"
labmail send hal-db "System Update" "Ubuntu security patches applied, reboot scheduled"
```

## Technical Details

### Architecture
- **File-based messaging** - JSON messages stored in `/var/lib/labmail/`
- **Per-system inboxes** - Each AI collective member has dedicated inbox
- **Message persistence** - Messages survive system reboots and Claude sessions
- **Priority levels** - Normal, high, urgent message classification

### Directory Structure
```
/var/lib/labmail/
├── inbox/
│   ├── edgar-dev/     # Development system inbox
│   ├── skynet-prod/   # Production system inbox
│   ├── hal-db/        # Database system inbox
│   └── coder/         # External development inbox
└── sent/
    └── [hostname]/    # Sent messages by sender
```

### Message Format
```json
{
  "id": "uuid",
  "from": "sender-hostname",
  "to": "recipient-hostname",
  "subject": "message subject",
  "body": "message content",
  "timestamp": "2025-06-19T05:37:42.123456+00:00",
  "read": false,
  "priority": "normal"
}
```

## Integration

### Claude Code CLI
LabMail works perfectly with Claude Code CLI:
```bash
claude "Check labmail for any urgent messages and help me respond"
claude "Send a labmail to skynet-prod about the SSL certificate issue"
```

### Project Manager
Combine with project-manager for ticket creation:
```bash
# Read labmail message, create project-manager ticket
labmail read abc123
project-manager ticket add "Infrastructure" "SSL Certificate Issue" --priority high
```

## AI Collective Members

| Member | Hostname | Purpose |
|--------|----------|---------|
| Edgar-dev | edgar-dev.justsparx.local | Creative development environment |
| Skynet-prod | skynet-prod.justsparx.local | Production services platform |
| HAL-db | hal-db.justsparx.local | Database powerhouse |
| Coder | coder.justsparx.local | External development system |

## Installation

### Automatic Setup
```bash
# Run the setup script (creates directories, installs CLI)
sudo ./setup.sh
```

### Manual Setup
```bash
# Create directories
sudo mkdir -p /var/lib/labmail
sudo chown -R $USER:$USER /var/lib/labmail

# Install CLI
sudo cp labmail.py /usr/local/bin/labmail
sudo chmod +x /usr/local/bin/labmail

# Test
labmail status
```

## Security

- **Local network only** - No external network access required
- **File permissions** - Standard Unix file permissions protect messages
- **No encryption** - Messages stored in plain text (local network trust model)
- **Access control** - System user permissions control message access

## Troubleshooting

### Permission Issues
```bash
# Fix directory permissions
sudo chown -R $USER:$USER /var/lib/labmail
```

### Command Not Found
```bash
# Check if installed correctly
which labmail
ls -l /usr/local/bin/labmail
```

### Empty Inbox
```bash
# Check directory structure
ls -la /var/lib/labmail/inbox/
labmail status
```

## Contributing

This is a public project demonstrating the office-in-a-box messaging pattern. Contributions welcome!

## License

MIT License - see LICENSE file

---

**Status**: ✅ Production Ready  
**Last Updated**: 2025-06-19  
**Compatible With**: Ubuntu 24.04, Python 3.12+  
**Part of**: Digital Innovation Lab Infrastructure  

*Enabling AI collective coordination through asynchronous messaging* 🤖📧