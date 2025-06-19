#!/usr/bin/env python3
"""
LabMail - Digital Innovation Lab Messaging System (PostgreSQL Backend)
Interoffice messaging for AI collective coordination via HAL-db PostgreSQL
"""

import argparse
import json
import os
import socket
import sys
import uuid
from datetime import datetime, timezone
import psycopg2
from psycopg2.extras import RealDictCursor


class LabMailDB:
    def __init__(self):
        self.hostname = socket.gethostname().split('.')[0]  # Remove domain
        
        # HAL-db connection settings
        self.db_config = {
            'host': '192.168.1.202',  # hal-db.justsparx.local
            'port': 5432,
            'database': 'hal_main',
            'user': 'hal_admin',
            'password': 'hal_admin_password'
        }
        
        # Known AI collective members
        self.collective_members = [
            "edgar-dev", "skynet-prod", "hal-db", "coder"
        ]
        
        self._ensure_tables()
    
    def _get_connection(self):
        """Get database connection to HAL-db"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            print(f"❌ Cannot connect to HAL-db: {e}")
            print(f"   Host: {self.db_config['host']}:{self.db_config['port']}")
            print(f"   Database: {self.db_config['database']}")
            print("   Ensure HAL-db is running and accessible")
            sys.exit(1)
    
    def _ensure_tables(self):
        """Create LabMail tables if they don't exist"""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            # Create messages table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS labmail_messages (
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
            """)
            
            # Create index for efficient queries
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_labmail_to_system 
                ON labmail_messages(to_system, is_read, created_at DESC);
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_labmail_from_system 
                ON labmail_messages(from_system, created_at DESC);
            """)
            
            conn.commit()
            
        except psycopg2.Error as e:
            print(f"❌ Database setup error: {e}")
            sys.exit(1)
        finally:
            conn.close()
    
    def send_message(self, recipient, subject, body, priority="normal"):
        """Send a message to a recipient via HAL-db"""
        # Clean recipient name
        recipient = recipient.split('.')[0]  # Remove domain if present
        
        if recipient not in self.collective_members:
            print(f"❌ Unknown recipient: {recipient}")
            print(f"Available recipients: {', '.join(self.collective_members)}")
            return False
        
        message_id = str(uuid.uuid4())
        
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO labmail_messages 
                (id, from_system, to_system, subject, body, priority)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (message_id, self.hostname, recipient, subject, body, priority))
            
            conn.commit()
            
            priority_emoji = {"normal": "📧", "high": "⚡", "urgent": "🚨"}
            print(f"{priority_emoji.get(priority, '📧')} Message sent to {recipient} via HAL-db")
            print(f"   Subject: {subject}")
            print(f"   ID: {message_id[:8]}...")
            return True
            
        except psycopg2.Error as e:
            print(f"❌ Error sending message: {e}")
            return False
        finally:
            conn.close()
    
    def list_messages(self, unread_only=False, from_sender=None):
        """List messages in inbox from HAL-db"""
        conn = self._get_connection()
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Build query
            query = """
                SELECT id, from_system, subject, priority, created_at, is_read
                FROM labmail_messages 
                WHERE to_system = %s
            """
            params = [self.hostname]
            
            if unread_only:
                query += " AND is_read = FALSE"
            
            if from_sender:
                query += " AND from_system = %s"
                params.append(from_sender.split('.')[0])
            
            query += " ORDER BY created_at DESC"
            
            cur.execute(query, params)
            messages = cur.fetchall()
            
            if not messages:
                filter_desc = []
                if unread_only:
                    filter_desc.append("unread")
                if from_sender:
                    filter_desc.append(f"from {from_sender}")
                
                filter_text = " ".join(filter_desc) if filter_desc else ""
                print(f"📬 No {filter_text} messages" if filter_text else "📬 No messages")
                return
            
            print(f"📬 {len(messages)} message(s) in inbox:")
            print()
            
            for msg in messages:
                status = "📭" if msg['is_read'] else "📬"
                priority = {"high": "⚡", "urgent": "🚨"}.get(msg['priority'], "")
                
                timestamp = msg['created_at'].strftime('%Y-%m-%d %H:%M')
                
                print(f"{status} {priority} [{str(msg['id'])[:8]}] From: {msg['from_system']}")
                print(f"    📅 {timestamp}")
                print(f"    📋 {msg['subject']}")
                print()
                
        except psycopg2.Error as e:
            print(f"❌ Error listing messages: {e}")
        finally:
            conn.close()
    
    def read_message(self, message_id=None, unread_only=False):
        """Read a specific message or show unread messages"""
        if message_id:
            # Read specific message
            conn = self._get_connection()
            try:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                
                # Find message by partial ID
                cur.execute("""
                    SELECT * FROM labmail_messages 
                    WHERE to_system = %s AND CAST(id AS TEXT) LIKE %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (self.hostname, f"{message_id}%"))
                
                message = cur.fetchone()
                
                if not message:
                    print(f"❌ Message not found: {message_id}")
                    return
                
                self._display_message(dict(message))
                
                # Mark as read
                cur.execute("""
                    UPDATE labmail_messages 
                    SET is_read = TRUE, read_at = NOW()
                    WHERE id = %s
                """, (message['id'],))
                
                conn.commit()
                
            except psycopg2.Error as e:
                print(f"❌ Error reading message: {e}")
            finally:
                conn.close()
        else:
            # Show unread messages
            self.list_messages(unread_only=True)
    
    def _display_message(self, message):
        """Display a message in detail"""
        priority_emoji = {"normal": "📧", "high": "⚡", "urgent": "🚨"}
        timestamp = message['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"{priority_emoji.get(message['priority'], '📧')} Message Details")
        print("=" * 50)
        print(f"📨 From: {message['from_system']}")
        print(f"📅 Date: {timestamp}")
        print(f"🆔 ID: {message['id']}")
        print(f"📋 Subject: {message['subject']}")
        print()
        print("📝 Message:")
        print("-" * 30)
        print(message['body'] or 'No content')
        print("-" * 30)
        print()
    
    def get_status(self):
        """Show LabMail system status"""
        print(f"🤖 LabMail Status - {self.hostname}")
        print("=" * 40)
        
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            # Count messages
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE is_read = FALSE) as unread
                FROM labmail_messages 
                WHERE to_system = %s
            """, (self.hostname,))
            
            counts = cur.fetchone()
            total_messages = counts[0] if counts else 0
            unread_messages = counts[1] if counts else 0
            
            print(f"📬 Total messages: {total_messages}")
            print(f"📭 Unread messages: {unread_messages}")
            print(f"🏠 Hostname: {self.hostname}")
            print(f"🗄️ Database: HAL-db PostgreSQL ({self.db_config['host']})")
            
            # Test database connection
            cur.execute("SELECT version()")
            db_version = cur.fetchone()[0].split(' ')[0:2]
            print(f"💾 Database: {' '.join(db_version)}")
            
            print()
            print("🤖 AI Collective Members:")
            for member in self.collective_members:
                print(f"   🤖 {member}")
                
        except psycopg2.Error as e:
            print(f"❌ Database error: {e}")
        finally:
            conn.close()
    
    def get_stats(self):
        """Show message statistics across AI collective"""
        conn = self._get_connection()
        try:
            cur = conn.cursor()
            
            print("📊 LabMail System Statistics")
            print("=" * 40)
            
            # Total messages in system
            cur.execute("SELECT COUNT(*) FROM labmail_messages")
            total = cur.fetchone()[0]
            print(f"📧 Total messages in system: {total}")
            
            # Messages by sender
            cur.execute("""
                SELECT from_system, COUNT(*) as count
                FROM labmail_messages 
                GROUP BY from_system 
                ORDER BY count DESC
            """)
            
            print("\n📤 Messages sent by system:")
            for row in cur.fetchall():
                print(f"   🤖 {row[0]}: {row[1]} messages")
            
            # Messages by recipient
            cur.execute("""
                SELECT to_system, COUNT(*) as count
                FROM labmail_messages 
                GROUP BY to_system 
                ORDER BY count DESC
            """)
            
            print("\n📥 Messages received by system:")
            for row in cur.fetchall():
                print(f"   🤖 {row[0]}: {row[1]} messages")
            
            # Unread messages by system
            cur.execute("""
                SELECT to_system, COUNT(*) as unread
                FROM labmail_messages 
                WHERE is_read = FALSE
                GROUP BY to_system 
                ORDER BY unread DESC
            """)
            
            unread_data = cur.fetchall()
            if unread_data:
                print("\n📭 Unread messages by system:")
                for row in unread_data:
                    print(f"   📬 {row[0]}: {row[1]} unread")
            else:
                print("\n✅ All messages read across AI collective!")
                
        except psycopg2.Error as e:
            print(f"❌ Database error: {e}")
        finally:
            conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="LabMail - Digital Innovation Lab Messaging System (PostgreSQL)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  labmail send skynet-prod "SSL Issue" "Please check SSL certificate configuration"
  labmail send edgar-dev "Testing Required" "New API endpoints ready for testing"
  labmail list --unread
  labmail read abc123
  labmail status
  labmail stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Send command
    send_parser = subparsers.add_parser('send', help='Send a message')
    send_parser.add_argument('recipient', help='Recipient hostname (edgar-dev, skynet-prod, hal-db, coder)')
    send_parser.add_argument('subject', help='Message subject')
    send_parser.add_argument('body', nargs='?', default='', help='Message body (optional)')
    send_parser.add_argument('--priority', choices=['normal', 'high', 'urgent'], default='normal',
                           help='Message priority (default: normal)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List messages')
    list_parser.add_argument('--unread', action='store_true', help='Show only unread messages')
    list_parser.add_argument('--from', dest='from_sender', help='Show messages from specific sender')
    
    # Read command
    read_parser = subparsers.add_parser('read', help='Read a message')
    read_parser.add_argument('message_id', nargs='?', help='Message ID to read (optional)')
    read_parser.add_argument('--unread', action='store_true', help='Show unread messages if no ID specified')
    
    # Status command
    subparsers.add_parser('status', help='Show LabMail system status')
    
    # Stats command  
    subparsers.add_parser('stats', help='Show system-wide message statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    labmail = LabMailDB()
    
    if args.command == 'send':
        if not args.body:
            # Interactive input for message body
            print("Enter message body (Ctrl+D or Ctrl+Z when done):")
            try:
                args.body = sys.stdin.read().strip()
            except KeyboardInterrupt:
                print("\n❌ Message cancelled")
                return
        
        labmail.send_message(args.recipient, args.subject, args.body, args.priority)
    
    elif args.command == 'list':
        labmail.list_messages(unread_only=args.unread, from_sender=args.from_sender)
    
    elif args.command == 'read':
        if args.message_id:
            labmail.read_message(args.message_id)
        else:
            labmail.read_message(unread_only=args.unread)
    
    elif args.command == 'status':
        labmail.get_status()
        
    elif args.command == 'stats':
        labmail.get_stats()


if __name__ == '__main__':
    main()