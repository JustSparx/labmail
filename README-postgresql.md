# LabMail PostgreSQL Architecture

## Database-Centric Messaging

LabMail now uses HAL-db PostgreSQL as the central messaging backend, providing:

### Benefits over File-Based Approach
✅ **Centralized storage** - All messages in HAL-db PostgreSQL  
✅ **No permission issues** - Database handles access control  
✅ **Concurrent access** - Multiple systems reading/writing safely  
✅ **SQL queries** - Advanced filtering and statistics  
✅ **Automatic backups** - Included in HAL's backup system  
✅ **Network resilience** - Proper database connections  

### Database Schema
```sql
CREATE TABLE labmail_messages (
    id UUID PRIMARY KEY,
    from_system VARCHAR(50) NOT NULL,
    to_system VARCHAR(50) NOT NULL,
    subject TEXT NOT NULL,
    body TEXT,
    priority VARCHAR(20) DEFAULT 'normal',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE NULL,
    is_read BOOLEAN DEFAULT FALSE
);

-- Indexes for efficient queries
CREATE INDEX idx_labmail_to_system ON labmail_messages(to_system, is_read, created_at DESC);
CREATE INDEX idx_labmail_from_system ON labmail_messages(from_system, created_at DESC);
```

### Network Architecture
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Edgar-dev   │    │ Skynet-prod │    │   Coder     │
│192.168.1.201│    │192.168.1.200│    │192.168.1.164│
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                 ┌────────▼────────┐
                 │    HAL-db       │
                 │ 192.168.1.202   │
                 │ PostgreSQL:5432 │
                 │   hal_main      │
                 └─────────────────┘
```

### Configuration Files

#### HAL-db PostgreSQL Setup
- **postgresql.conf**: `listen_addresses = '*'`
- **pg_hba.conf**: Host access for AI collective subnet
- **UFW firewall**: Port 5432 open for 192.168.1.0/24

#### Client Configuration
- **Connection**: `hal-db.justsparx.local:5432`
- **Database**: `hal_main`
- **User**: `hal_admin`
- **Authentication**: MD5 password

### Installation Steps

#### 1. Configure HAL-db (One-time setup)
```bash
# On HAL-db system
git clone https://github.com/JustSparx/labmail.git
cd labmail
sudo ./configure-hal-db.sh
```

#### 2. Install on AI Collective Members
```bash
# On each system (edgar-dev, skynet-prod, coder)
git clone https://github.com/JustSparx/labmail.git
cd labmail
sudo ./setup-db.sh
labmail status
```

### Advanced Commands

#### System Statistics
```bash
labmail stats  # Show system-wide message statistics
```

#### Message Filtering
```bash
labmail list --from edgar-dev     # Messages from specific sender
labmail list --unread            # Only unread messages
```

#### Database Queries (Advanced)
```sql
-- Connect to HAL-db directly for custom queries
PGPASSWORD='hal_admin_password' psql -h hal-db.justsparx.local -U hal_admin -d hal_main

-- Message volume by system
SELECT from_system, COUNT(*) as sent_count
FROM labmail_messages
GROUP BY from_system
ORDER BY sent_count DESC;

-- Recent activity
SELECT from_system, to_system, subject, created_at
FROM labmail_messages
ORDER BY created_at DESC
LIMIT 10;
```

### Troubleshooting

#### Connection Issues
```bash
# Test PostgreSQL connectivity
PGPASSWORD='hal_admin_password' psql -h 192.168.1.202 -U hal_admin -d hal_main -c "SELECT 'Connected!' as status;"

# Check HAL-db PostgreSQL service
ssh sparx@hal-db.justsparx.local
sudo systemctl status postgresql
sudo journalctl -u postgresql
```

#### Firewall Issues
```bash
# On HAL-db, check firewall
sudo ufw status | grep 5432

# Test network connectivity
telnet hal-db.justsparx.local 5432
```

#### Permission Issues
```bash
# Check pg_hba.conf on HAL-db
sudo cat /etc/postgresql/16/main/pg_hba.conf | grep hal_admin
```

### Migration from File-Based

The original file-based LabMail is preserved as `labmail.py` for compatibility. The PostgreSQL version is `labmail-db.py` and becomes the main `labmail` command after installation.

#### Backup Strategy
Messages in PostgreSQL benefit from:
- HAL-db automated daily backups
- PostgreSQL WAL logging
- Point-in-time recovery capabilities
- Standard database replication if needed

---

**Status**: ✅ Ready for deployment  
**Database**: HAL-db PostgreSQL 16  
**Network**: Configured for AI collective access  
**Backup**: Included in HAL-db backup system