#!/bin/bash
set -e  # Exit on any error

echo "🐘 HAL-db PostgreSQL Network Configuration for LabMail"
echo "===================================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "✅ Running with sudo privileges"
    SUDO_CMD=""
else
    echo "🔑 Checking sudo access..."
    sudo -v
    SUDO_CMD="sudo"
fi

# Find PostgreSQL version and config directory
PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP 'PostgreSQL \K[0-9]+')
PG_CONFIG_DIR="/etc/postgresql/$PG_VERSION/main"

echo "🔍 Detected PostgreSQL version: $PG_VERSION"
echo "📁 Config directory: $PG_CONFIG_DIR"

# Backup original configuration files
echo "💾 Creating configuration backups..."
$SUDO_CMD cp "$PG_CONFIG_DIR/postgresql.conf" "$PG_CONFIG_DIR/postgresql.conf.backup.$(date +%Y%m%d_%H%M%S)"
$SUDO_CMD cp "$PG_CONFIG_DIR/pg_hba.conf" "$PG_CONFIG_DIR/pg_hba.conf.backup.$(date +%Y%m%d_%H%M%S)"

# Configure PostgreSQL to listen on network interfaces
echo "🌐 Configuring PostgreSQL for network access..."
$SUDO_CMD sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONFIG_DIR/postgresql.conf"

# Also set port explicitly (should already be 5432)
$SUDO_CMD sed -i "s/#port = 5432/port = 5432/" "$PG_CONFIG_DIR/postgresql.conf"

# Configure pg_hba.conf for AI collective access
echo "🔐 Configuring client authentication for AI collective..."

# Add host entries for AI collective members
$SUDO_CMD tee -a "$PG_CONFIG_DIR/pg_hba.conf" > /dev/null << 'EOF'

# LabMail AI Collective Access
# Allow hal_admin user from AI collective members
host    hal_main        hal_admin       192.168.1.200/32        md5     # skynet-prod
host    hal_main        hal_admin       192.168.1.201/32        md5     # edgar-dev
host    hal_main        hal_admin       192.168.1.202/32        md5     # hal-db (local)
host    hal_main        hal_admin       192.168.1.164/32        md5     # coder
host    hal_main        hal_admin       192.168.1.0/24          md5     # entire subnet (flexible)
EOF

echo "✅ PostgreSQL configuration updated"

# Configure UFW firewall for PostgreSQL access
echo "🔥 Configuring firewall for PostgreSQL access..."

# Allow PostgreSQL from AI collective subnet
$SUDO_CMD ufw allow from 192.168.1.0/24 to any port 5432 comment 'LabMail PostgreSQL AI Collective'

echo "✅ Firewall configured for LabMail access"

# Restart PostgreSQL to apply changes
echo "🔄 Restarting PostgreSQL service..."
$SUDO_CMD systemctl restart postgresql

# Wait a moment for service to fully restart
sleep 3

# Test PostgreSQL service status
echo "🧪 Testing PostgreSQL service..."
if $SUDO_CMD systemctl is-active postgresql >/dev/null; then
    echo "✅ PostgreSQL service is running"
else
    echo "❌ PostgreSQL service failed to start"
    echo "Check logs: sudo journalctl -u postgresql"
    exit 1
fi

# Test local connection
echo "🔗 Testing local PostgreSQL connection..."
if sudo -u postgres psql -d hal_main -c "SELECT 'PostgreSQL connection successful!' as status;" >/dev/null; then
    echo "✅ Local PostgreSQL connection working"
else
    echo "❌ Local PostgreSQL connection failed"
    exit 1
fi

# Test hal_admin user connection
echo "👤 Testing hal_admin user connection..."
if PGPASSWORD='hal_admin_password' psql -h localhost -U hal_admin -d hal_main -c "SELECT 'hal_admin connection successful!' as status;" >/dev/null; then
    echo "✅ hal_admin user connection working"
else
    echo "❌ hal_admin user connection failed"
    echo "Checking if user exists..."
    sudo -u postgres psql -c "SELECT usename FROM pg_user WHERE usename='hal_admin';"
fi

# Display connection information
echo ""
echo "🎉 HAL-db PostgreSQL Configuration Complete!"
echo "============================================"
echo ""
echo "📊 Connection Details:"
echo "   Host: hal-db.justsparx.local (192.168.1.202)"
echo "   Port: 5432"
echo "   Database: hal_main"
echo "   User: hal_admin"
echo "   Password: hal_admin_password"
echo ""
echo "🤖 Authorized AI Collective Members:"
echo "   ✅ edgar-dev (192.168.1.201)"
echo "   ✅ skynet-prod (192.168.1.200)"
echo "   ✅ hal-db (192.168.1.202)"
echo "   ✅ coder (192.168.1.164)"
echo ""
echo "🔥 Firewall Rules:"
$SUDO_CMD ufw status | grep 5432 || echo "   (No specific rules shown - check with: sudo ufw status)"
echo ""
echo "📁 Configuration Files:"
echo "   PostgreSQL: $PG_CONFIG_DIR/postgresql.conf"
echo "   Auth: $PG_CONFIG_DIR/pg_hba.conf"
echo "   Backups: $PG_CONFIG_DIR/*.backup.*"
echo ""
echo "🧪 Test Network Connection from AI Collective:"
echo "   PGPASSWORD='hal_admin_password' psql -h 192.168.1.202 -U hal_admin -d hal_main -c \"SELECT 'Connected!' as status;\""
echo ""
echo "📦 Next Steps:"
echo "   1. Test connection from other AI collective members"
echo "   2. Deploy LabMail PostgreSQL version to all systems"
echo "   3. Run: labmail status (on each system)"
echo ""
echo "🗄️ HAL-db is now ready for AI collective messaging!"