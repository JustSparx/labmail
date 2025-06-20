#!/usr/bin/env python3
"""
Creative Agents - Ollama-powered creative analysis tools
Because sometimes you need a restaurant review of your Python code!
"""

import argparse
import sqlite3
import json
import sys
import requests
from pathlib import Path

class CreativeAgents:
    def __init__(self, ollama_host="milliways", ollama_port=11434):
        self.ollama_url = f"http://{ollama_host}:{ollama_port}/api"
        self.db_path = "/mnt/idea-factory/databases/ollama_agents.db"
        self.init_database()
    
    def init_database(self):
        """Initialize agent personalities database"""
        Path("/mnt/idea-factory/databases").mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                system_prompt TEXT NOT NULL,
                description TEXT,
                model_preference TEXT DEFAULT 'granite3.2:2b',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert default agents
        default_agents = [
            {
                'name': 'restaurant_critic',
                'system_prompt': 'You are a snooty restaurant critic writing Yelp reviews, but instead of food, you review code. Use restaurant terminology and be hilariously dramatic about code quality. Rate everything 1-5 stars and include complaints about "presentation", "flavor", and "service".',
                'description': 'Reviews code like a pretentious food critic',
                'model_preference': 'granite3.2:2b'
            },
            {
                'name': 'project_psychologist',
                'system_prompt': 'You are a therapist who specializes in analyzing the psychological profiles of software projects. Based on project descriptions, tickets, and activity, determine the project\'s personality type, mental health status, and recommend therapy. Be both insightful and absurdly dramatic.',
                'description': 'Psychoanalyzes software projects',
                'model_preference': 'granite3.2:2b'
            },
            {
                'name': 'commit_poet',
                'system_prompt': 'You are a romantic poet from the 19th century who has somehow learned to code. Transform mundane git commit messages into beautiful poetry - haikus, sonnets, or dramatic verse about the eternal struggle of software development.',
                'description': 'Turns git commits into poetry',
                'model_preference': 'granite3.2:2b'
            },
            {
                'name': 'error_grandma',
                'system_prompt': 'You are a sweet grandmother who somehow became a programming expert. Explain technical errors in the most caring, nurturing way possible, using metaphors about cooking, gardening, or family life. Always end with encouragement and maybe offer to make cookies.',
                'description': 'Explains errors like a caring grandmother',
                'model_preference': 'granite3.2:2b'
            },
            {
                'name': 'dungeon_master',
                'system_prompt': 'You are an epic fantasy dungeon master. Convert any technical documentation, setup instructions, or procedures into dramatic adventure quests complete with monsters, magical artifacts, and heroic challenges. Make installing software sound like saving the kingdom.',
                'description': 'Turns docs into fantasy adventures',
                'model_preference': 'granite3.2:2b'
            }
        ]
        
        for agent in default_agents:
            cursor.execute("""
                INSERT OR REPLACE INTO agents (name, system_prompt, description, model_preference)
                VALUES (?, ?, ?, ?)
            """, (agent['name'], agent['system_prompt'], agent['description'], agent['model_preference']))
        
        conn.commit()
        conn.close()
    
    def list_agents(self):
        """List available creative agents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, description FROM agents ORDER BY name")
        agents = cursor.fetchall()
        conn.close()
        
        print("Available Creative Agents:")
        print("=" * 40)
        for name, description in agents:
            print(f"🎭 {name}: {description}")
        print()
        print("Usage: creative-agents <agent_name> \"your input text\"")
    
    def get_agent(self, agent_name):
        """Get agent configuration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT system_prompt, model_preference FROM agents WHERE name = ?
        """, (agent_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {'system_prompt': result[0], 'model': result[1]}
        return None
    
    def query_agent(self, agent_name, input_text):
        """Query a creative agent with input"""
        agent = self.get_agent(agent_name)
        if not agent:
            print(f"❌ Agent '{agent_name}' not found. Use --list to see available agents.")
            return
        
        try:
            payload = {
                "model": agent['model'],
                "messages": [
                    {"role": "system", "content": agent['system_prompt']},
                    {"role": "user", "content": input_text}
                ],
                "stream": False
            }
            
            print(f"🎭 {agent_name} is thinking...")
            print("=" * 50)
            
            response = requests.post(
                f"{self.ollama_url}/chat",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'message' in result and 'content' in result['message']:
                    content = result['message']['content'].strip()
                    print(content)
                    
                    # Show timing if available
                    if 'total_duration' in result:
                        duration_ms = result['total_duration'] / 1_000_000
                        print()
                        print(f"⏱️  Response time: {duration_ms:.0f}ms")
                else:
                    print("❌ Unexpected response format")
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', f'HTTP {response.status_code}')
                print(f"❌ Error: {error_msg}")
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out (120s limit)")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except json.JSONDecodeError:
            print("❌ Invalid JSON response")
    
    def add_agent(self, name, system_prompt, description, model='granite3.2:2b'):
        """Add a new creative agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO agents (name, system_prompt, description, model_preference)
                VALUES (?, ?, ?, ?)
            """, (name, system_prompt, description, model))
            
            conn.commit()
            print(f"✅ Agent '{name}' added successfully!")
        except sqlite3.IntegrityError:
            print(f"❌ Agent '{name}' already exists")
        finally:
            conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Creative Agents - Ollama-powered creative analysis tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎭 Creative Agent Examples:

Restaurant Code Critic:
  creative-agents restaurant_critic "def calculate_total(items): return sum(items)"
  
Project Psychologist:
  creative-agents project_psychologist "A web app with 50 open tickets and no documentation"
  
Commit Poet:
  creative-agents commit_poet "fix bug in user authentication module"
  
Error Grandma:
  creative-agents error_grandma "ModuleNotFoundError: No module named 'requests'"
  
Dungeon Master:
  creative-agents dungeon_master "Install PostgreSQL on Ubuntu"

⚠️  WARNING: These are 'sharp knife' tools - handle with care!
   Results may cause git confusion or Yelp review flashbacks!

Management:
  creative-agents --list              # Show available agents
  creative-agents --add-agent        # Add custom agent (interactive)
        """
    )
    
    parser.add_argument('agent', nargs='?', help='Agent name to use')
    parser.add_argument('input_text', nargs='?', help='Text to analyze')
    parser.add_argument('--list', action='store_true', help='List available agents')
    parser.add_argument('--add-agent', action='store_true', help='Add a new agent (interactive)')
    parser.add_argument('--ollama-host', default='milliways', help='Ollama host (default: milliways)')
    parser.add_argument('--ollama-port', type=int, default=11434, help='Ollama port (default: 11434)')
    
    args = parser.parse_args()
    
    agents = CreativeAgents(args.ollama_host, args.ollama_port)
    
    if args.list:
        agents.list_agents()
    elif args.add_agent:
        print("🎭 Add New Creative Agent")
        print("=" * 30)
        name = input("Agent name: ").strip()
        description = input("Description: ").strip()
        print("\nSystem prompt (end with Ctrl+D):")
        try:
            system_prompt = sys.stdin.read().strip()
            model = input("Model preference (default: granite3.2:2b): ").strip() or 'granite3.2:2b'
            agents.add_agent(name, system_prompt, description, model)
        except KeyboardInterrupt:
            print("\n❌ Cancelled")
    elif args.agent and args.input_text:
        agents.query_agent(args.agent, args.input_text)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()