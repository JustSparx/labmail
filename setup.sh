#!/bin/bash
set -e  # Exit on any error

echo "🚀 LabMail - Digital Innovation Lab Messaging Setup"
echo "=================================================="

# Check if running as root for directory creation
if [[ $EUID -eq 0 ]]; then
    echo "✅ Running with sudo privileges"
    SUDO_CMD=""
else
    echo "🔑 Checking sudo access..."
    sudo -v
    SUDO_CMD="sudo"
fi

# Create LabMail directories
echo "📁 Creating LabMail directories..."
$SUDO_CMD mkdir -p /var/lib/labmail/inbox
$SUDO_CMD mkdir -p /var/lib/labmail/sent

# Create inbox directories for AI collective members
echo "🤖 Setting up AI collective member inboxes..."
for member in edgar-dev skynet-prod hal-db coder; do
    $SUDO_CMD mkdir -p "/var/lib/labmail/inbox/$member"
    echo "   ✅ $member inbox created"
done

# Set proper ownership
echo "🔧 Setting directory ownership..."
$SUDO_CMD chown -R $USER:$USER /var/lib/labmail

# Install LabMail CLI
echo "📦 Installing LabMail CLI..."
$SUDO_CMD cp labmail.py /usr/local/bin/labmail
$SUDO_CMD chmod +x /usr/local/bin/labmail

# Verify installation
echo "🧪 Testing installation..."
if command -v labmail >/dev/null 2>&1; then
    echo "✅ LabMail CLI installed successfully!"
    
    # Show status
    echo ""
    echo "🤖 LabMail System Status:"
    labmail status
    
    echo ""
    echo "🎉 LabMail setup complete!"
    echo ""
    echo "Usage examples:"
    echo "  labmail send skynet-prod \"Test Message\" \"Hello from LabMail!\""
    echo "  labmail list"
    echo "  labmail read --unread"
    echo "  labmail status"
    echo ""
    echo "📖 See README.md for complete documentation"
else
    echo "❌ Installation failed - labmail command not found"
    exit 1
fi