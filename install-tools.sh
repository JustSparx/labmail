#!/bin/bash
# AI Collective Shared Tools Installation Script
# Adds /mnt/idea-factory/bin to PATH and creates local symlinks

echo "AI Collective Shared Tools Installation"
echo "======================================="

# Check if NFS mount exists
if [ ! -d "/mnt/idea-factory/bin" ]; then
    echo "ERROR: /mnt/idea-factory/bin not found"
    echo "Ensure NFS idea-factory is mounted first"
    exit 1
fi

# Add to PATH in .bashrc if not already present
if ! grep -q "/mnt/idea-factory/bin" ~/.bashrc; then
    echo 'export PATH="/mnt/idea-factory/bin:$PATH"' >> ~/.bashrc
    echo "✅ Added /mnt/idea-factory/bin to PATH in ~/.bashrc"
else
    echo "✅ /mnt/idea-factory/bin already in PATH"
fi

# Create symlinks in /usr/local/bin (requires sudo)
echo ""
echo "Creating system-wide symlinks (requires sudo):"

if [ -f "/mnt/idea-factory/bin/labmail" ]; then
    if [ ! -L "/usr/local/bin/labmail" ]; then
        echo -n "Creating /usr/local/bin/labmail symlink... "
        if sudo ln -s /mnt/idea-factory/bin/labmail /usr/local/bin/labmail 2>/dev/null; then
            echo "✅ Done"
        else
            echo "❌ Failed (sudo required)"
        fi
    else
        echo "✅ /usr/local/bin/labmail already exists"
    fi
fi

if [ -f "/mnt/idea-factory/bin/labmail-ai" ]; then
    if [ ! -L "/usr/local/bin/labmail-ai" ]; then
        echo -n "Creating /usr/local/bin/labmail-ai symlink... "
        if sudo ln -s /mnt/idea-factory/bin/labmail-ai /usr/local/bin/labmail-ai 2>/dev/null; then
            echo "✅ Done"
        else
            echo "❌ Failed (sudo required)"
        fi
    else
        echo "✅ /usr/local/bin/labmail-ai already exists"
    fi
fi

echo ""
echo "Installation complete!"
echo ""
echo "Available tools:"
for tool in /mnt/idea-factory/bin/*; do
    if [ -x "$tool" ] && [ ! -d "$tool" ]; then
        basename "$tool"
    fi
done

echo ""
echo "Usage:"
echo "  Source new PATH: source ~/.bashrc"
echo "  Or start new shell session"
echo "  Then use: labmail send hal-db \"Test\" \"Message\""
echo ""
echo "System hostname: $(hostname)"
echo "NFS mount status: $(if mountpoint -q /mnt/idea-factory; then echo 'Mounted'; else echo 'Not mounted'; fi)"