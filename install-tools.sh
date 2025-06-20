#!/bin/bash
# AI Collective Shared Tools Installation Script
# Adds /mnt/idea-factory/bin to PATH (clean approach - no symlinks)

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

# Note: Using PATH instead of symlinks for cleaner shared tool management
echo ""
echo "✅ Tools will be available via PATH after shell restart"

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
echo "Alternative - Direct execution (no setup needed):"
echo "  /mnt/idea-factory/bin/labmail send hal-db \"Test\" \"Message\""
echo ""
echo "System hostname: $(hostname)"
echo "NFS mount status: $(if mountpoint -q /mnt/idea-factory; then echo 'Mounted'; else echo 'Not mounted'; fi)"