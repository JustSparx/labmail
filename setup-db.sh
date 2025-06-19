#!/bin/bash
set -e  # Exit on any error

echo "🚀 LabMail PostgreSQL - Digital Innovation Lab Messaging Setup"
echo "============================================================"

# Check if running as root for directory creation
if [[ $EUID -eq 0 ]]; then
    echo "✅ Running with sudo privileges"
    SUDO_CMD=""
else
    echo "🔑 Checking sudo access..."
    sudo -v
    SUDO_CMD="sudo"
fi

# Install LabMail PostgreSQL CLI
echo "📦 Installing LabMail PostgreSQL CLI..."
$SUDO_CMD cp labmail-db.py /usr/local/bin/labmail
$SUDO_CMD chmod +x /usr/local/bin/labmail

# Install Python PostgreSQL dependency if needed
echo "🐍 Checking Python PostgreSQL dependency..."
python3 -c "import psycopg2" 2>/dev/null || {
    echo "📦 Installing psycopg2 for PostgreSQL connectivity..."
    
    # Check if in virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        pip install psycopg2-binary
    else
        # Try user install first
        pip3 install --user psycopg2-binary || {
            echo "Installing system-wide with sudo..."
            $SUDO_CMD pip3 install psycopg2-binary
        }
    fi
}

# Test HAL-db connectivity
echo "🔗 Testing HAL-db connectivity..."
if python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='hal-db.justsparx.local',
        port=5432,
        database='hal_main',
        user='hal_admin',
        password='hal_admin_password'
    )
    print('✅ HAL-db connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ HAL-db connection failed: {e}')
    exit(1)
"; then
    echo "🗄️ HAL-db PostgreSQL backend ready!"
else
    echo "❌ Cannot connect to HAL-db. Ensure:"
    echo "   - HAL-db system is running"
    echo "   - PostgreSQL service is active"
    echo "   - Network connectivity to hal-db.justsparx.local:5432"
    exit 1
fi

# Verify installation
echo "🧪 Testing LabMail installation..."
if command -v labmail >/dev/null 2>&1; then
    echo "✅ LabMail PostgreSQL CLI installed successfully!"
    
    # Show status
    echo ""
    echo "🤖 LabMail System Status:"
    labmail status
    
    echo ""
    echo "🎉 LabMail PostgreSQL setup complete!"
    echo ""
    echo "Usage examples:"
    echo "  labmail send skynet-prod \"Test Message\" \"Hello from LabMail PostgreSQL!\""
    echo "  labmail list --unread"
    echo "  labmail read abc123"
    echo "  labmail stats"
    echo ""
    echo "📖 See README.md for complete documentation"
    echo "🗄️ All messages stored in HAL-db PostgreSQL for reliability!"
else
    echo "❌ Installation failed - labmail command not found"
    exit 1
fi