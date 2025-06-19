#!/usr/bin/env python3
"""
LabMail - Digital Innovation Lab Messaging System
Interoffice messaging for AI collective coordination across Claude Code sessions
"""

import argparse
import json
import os
import socket
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


class LabMail:
    def __init__(self):
        self.base_dir = Path("/var/lib/labmail")
        self.inbox_dir = self.base_dir / "inbox"
        self.sent_dir = self.base_dir / "sent"
        self.hostname = socket.gethostname()
        
        # Known AI collective members
        self.collective_members = [
            "edgar-dev", "skynet-prod", "hal-db", "coder",
            "edgar-dev.justsparx.local", "skynet-prod.justsparx.local", 
            "hal-db.justsparx.local", "coder.justsparx.local"
        ]
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.inbox_dir.mkdir(exist_ok=True)
            self.sent_dir.mkdir(exist_ok=True)
            
            # Create inbox directories for all collective members
            for member in self.collective_members:
                (self.inbox_dir / member.split('.')[0]).mkdir(exist_ok=True)
                
            # Create sent directory for this host
            (self.sent_dir / self.hostname.split('.')[0]).mkdir(exist_ok=True)
            
        except PermissionError:
            print("❌ Permission denied. LabMail directories need to be created with sudo.")
            print("Run: sudo mkdir -p /var/lib/labmail && sudo chown -R $USER:$USER /var/lib/labmail")
            sys.exit(1)
    
    def _create_message(self, to, subject, body, priority="normal"):
        """Create a message object"""
        return {
            "id": str(uuid.uuid4()),
            "from": self.hostname,
            "to": to,
            "subject": subject,
            "body": body,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "read": False,
            "priority": priority
        }
    
    def _save_message(self, message, is_sent=False):
        """Save message to appropriate directory"""
        if is_sent:
            # Save to sent directory
            sent_dir = self.sent_dir / self.hostname.split('.')[0]
            filename = f"{message['id']}.json"
            filepath = sent_dir / filename
        else:
            # Save to recipient's inbox
            recipient = message['to'].split('.')[0]  # Remove domain if present
            inbox_dir = self.inbox_dir / recipient
            filename = f"{message['id']}.json"
            filepath = inbox_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(message, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving message: {e}")
            return False
    
    def send_message(self, recipient, subject, body, priority="normal"):
        """Send a message to a recipient"""
        # Clean recipient name
        recipient = recipient.split('.')[0]  # Remove domain if present
        
        if recipient not in [m.split('.')[0] for m in self.collective_members]:
            print(f"❌ Unknown recipient: {recipient}")
            print(f"Available recipients: {', '.join(set([m.split('.')[0] for m in self.collective_members]))}")
            return False
        
        message = self._create_message(recipient, subject, body, priority)
        
        # Save to recipient's inbox
        if self._save_message(message):
            # Save copy to sent folder
            self._save_message(message, is_sent=True)
            
            priority_emoji = {"normal": "📧", "high": "⚡", "urgent": "🚨"}
            print(f"{priority_emoji.get(priority, '📧')} Message sent to {recipient}")
            print(f"   Subject: {subject}")
            print(f"   ID: {message['id'][:8]}...")
            return True
        
        return False
    
    def list_messages(self, unread_only=False, from_sender=None):
        """List messages in inbox"""
        my_inbox = self.inbox_dir / self.hostname.split('.')[0]
        
        if not my_inbox.exists():
            print("📬 No messages")
            return
        
        messages = []
        for msg_file in my_inbox.glob("*.json"):
            try:
                with open(msg_file, 'r') as f:
                    message = json.load(f)
                    
                if unread_only and message.get('read', False):
                    continue
                    
                if from_sender and message.get('from', '').split('.')[0] != from_sender.split('.')[0]:
                    continue
                    
                messages.append(message)
            except Exception as e:
                print(f"⚠️  Error reading message {msg_file}: {e}")
        
        if not messages:
            filter_desc = []
            if unread_only:
                filter_desc.append("unread")
            if from_sender:
                filter_desc.append(f"from {from_sender}")
            
            filter_text = " ".join(filter_desc) if filter_desc else ""
            print(f"📬 No {filter_text} messages" if filter_text else "📬 No messages")
            return
        
        # Sort by timestamp (newest first)
        messages.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        print(f"📬 {len(messages)} message(s) in inbox:")
        print()
        
        for msg in messages:
            status = "📭" if msg.get('read', False) else "📬"
            priority = {"high": "⚡", "urgent": "🚨"}.get(msg.get('priority', 'normal'), "")
            
            timestamp = datetime.fromisoformat(msg.get('timestamp', '')).strftime('%Y-%m-%d %H:%M')
            
            print(f"{status} {priority} [{msg['id'][:8]}] From: {msg.get('from', 'Unknown')}")
            print(f"    📅 {timestamp}")
            print(f"    📋 {msg.get('subject', 'No subject')}")
            print()
    
    def read_message(self, message_id=None, unread_only=False):
        """Read a specific message or show unread messages"""
        my_inbox = self.inbox_dir / self.hostname.split('.')[0]
        
        if not my_inbox.exists():
            print("📬 No messages")
            return
        
        if message_id:
            # Read specific message
            for msg_file in my_inbox.glob("*.json"):
                try:
                    with open(msg_file, 'r') as f:
                        message = json.load(f)
                    
                    if message['id'].startswith(message_id):
                        self._display_message(message)
                        
                        # Mark as read
                        message['read'] = True
                        with open(msg_file, 'w') as f:
                            json.dump(message, f, indent=2)
                        return
                        
                except Exception as e:
                    print(f"⚠️  Error reading message {msg_file}: {e}")
            
            print(f"❌ Message not found: {message_id}")
        else:
            # Show unread messages
            self.list_messages(unread_only=True)
    
    def _display_message(self, message):
        """Display a message in detail"""
        priority_emoji = {"normal": "📧", "high": "⚡", "urgent": "🚨"}
        timestamp = datetime.fromisoformat(message.get('timestamp', '')).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"{priority_emoji.get(message.get('priority', 'normal'), '📧')} Message Details")
        print("=" * 50)
        print(f"📨 From: {message.get('from', 'Unknown')}")
        print(f"📅 Date: {timestamp}")
        print(f"🆔 ID: {message.get('id', 'Unknown')}")
        print(f"📋 Subject: {message.get('subject', 'No subject')}")
        print()
        print("📝 Message:")
        print("-" * 30)
        print(message.get('body', 'No content'))
        print("-" * 30)
        print()
    
    def get_status(self):
        """Show LabMail system status"""
        my_inbox = self.inbox_dir / self.hostname.split('.')[0]
        
        print(f"🤖 LabMail Status - {self.hostname}")
        print("=" * 40)
        
        # Count messages
        total_messages = 0
        unread_messages = 0
        
        if my_inbox.exists():
            for msg_file in my_inbox.glob("*.json"):
                try:
                    with open(msg_file, 'r') as f:
                        message = json.load(f)
                    total_messages += 1
                    if not message.get('read', False):
                        unread_messages += 1
                except:
                    continue
        
        print(f"📬 Total messages: {total_messages}")
        print(f"📭 Unread messages: {unread_messages}")
        print(f"🏠 Hostname: {self.hostname}")
        print(f"📁 Mail directory: {self.base_dir}")
        print()
        print("🤖 AI Collective Members:")
        for member in sorted(set([m.split('.')[0] for m in self.collective_members])):
            inbox_exists = (self.inbox_dir / member).exists()
            status = "✅" if inbox_exists else "📋"
            print(f"   {status} {member}")


def main():
    parser = argparse.ArgumentParser(
        description="LabMail - Digital Innovation Lab Messaging System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  labmail send skynet-prod "SSL Issue" "Please check SSL certificate configuration"
  labmail send edgar-dev "Testing Required" "New API endpoints ready for testing"
  labmail list --unread
  labmail read abc123
  labmail status
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
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    labmail = LabMail()
    
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


if __name__ == '__main__':
    main()