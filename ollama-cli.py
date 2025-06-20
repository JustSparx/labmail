#!/usr/bin/env python3
"""
Ollama CLI - Quick AI queries via local Ollama API
One-shot queries perfect for Claude Code development sessions
"""

import argparse
import json
import sys
import requests
from datetime import datetime

class OllamaCLI:
    def __init__(self, host="milliways", port=11434):
        self.base_url = f"http://{host}:{port}/api"
        self.host = host
        self.port = port
    
    def list_models(self):
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    print("Available models:")
                    for model in models:
                        name = model.get('name', 'unknown')
                        size = model.get('size', 0)
                        size_gb = round(size / (1024**3), 1) if size > 0 else 0
                        print(f"  {name} ({size_gb}GB)")
                else:
                    print("No models available")
            else:
                print(f"ERROR: Failed to fetch models ({response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Cannot connect to Ollama at {self.host}:{self.port}")
            print(f"Details: {e}")
    
    def generate(self, model, prompt, stream=False):
        """Generate response from model"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream
            }
            
            print(f"Querying {model} on {self.host}...")
            print("=" * 50)
            
            response = requests.post(
                f"{self.base_url}/generate", 
                json=payload,
                timeout=120  # 2 minute timeout for large responses
            )
            
            if response.status_code == 200:
                result = response.json()
                output = result.get('response', '').strip()
                
                if output:
                    print(output)
                else:
                    print("No response generated")
                
                # Show timing info if available
                if 'total_duration' in result:
                    duration_ms = result['total_duration'] / 1_000_000  # nanoseconds to ms
                    print()
                    print(f"Response time: {duration_ms:.0f}ms")
                
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', f'HTTP {response.status_code}')
                print(f"ERROR: {error_msg}")
                
        except requests.exceptions.Timeout:
            print("ERROR: Request timed out (120s limit)")
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Request failed: {e}")
        except json.JSONDecodeError:
            print("ERROR: Invalid JSON response")
    
    def chat(self, model, message, system_prompt=None):
        """Chat-style interaction (future: add history)"""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": message})
            
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            
            print(f"Chat with {model} on {self.host}...")
            print("=" * 50)
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'message' in result:
                    content = result['message'].get('content', '').strip()
                    if content:
                        print(content)
                    else:
                        print("No response generated")
                else:
                    print("Unexpected response format")
                
                # Show timing info
                if 'total_duration' in result:
                    duration_ms = result['total_duration'] / 1_000_000
                    print()
                    print(f"Response time: {duration_ms:.0f}ms")
                    
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error', f'HTTP {response.status_code}')
                print(f"ERROR: {error_msg}")
                
        except requests.exceptions.Timeout:
            print("ERROR: Request timed out (120s limit)")
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Request failed: {e}")
        except json.JSONDecodeError:
            print("ERROR: Invalid JSON response")
    
    def status(self):
        """Show Ollama server status"""
        try:
            # Try a simple request to check if server is alive
            response = requests.get(f"{self.base_url}/tags", timeout=5)
            if response.status_code == 200:
                print(f"✅ Ollama server running at {self.host}:{self.port}")
                
                models = response.json().get('models', [])
                print(f"📦 {len(models)} models available")
                
                # Show system info if available
                try:
                    info_response = requests.get(f"http://{self.host}:{self.port}/api/version", timeout=5)
                    if info_response.status_code == 200:
                        version_info = info_response.json()
                        print(f"🔧 Version: {version_info.get('version', 'unknown')}")
                except:
                    pass
            else:
                print(f"❌ Ollama server responded with status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to Ollama at {self.host}:{self.port}")
            print(f"Details: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Ollama CLI - Quick AI queries for development sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick query
  ollama-cli "Explain this error: ModuleNotFoundError"
  
  # Specific model
  ollama-cli -m llama3.2 "Write a Python function to parse JSON"
  
  # Chat mode with system prompt
  ollama-cli -c -s "You are a helpful coding assistant" "Debug this Python code"
  
  # List available models
  ollama-cli -l
  
  # Check server status
  ollama-cli --status

Default host: milliways:11434
        """
    )
    
    parser.add_argument('prompt', nargs='?', help='Query/prompt for the AI model')
    parser.add_argument('-m', '--model', default='llama3.2', help='Model to use (default: llama3.2)')
    parser.add_argument('-H', '--host', default='milliways', help='Ollama host (default: milliways)')
    parser.add_argument('-p', '--port', type=int, default=11434, help='Ollama port (default: 11434)')
    parser.add_argument('-l', '--list', action='store_true', help='List available models')
    parser.add_argument('-c', '--chat', action='store_true', help='Use chat mode instead of generate')
    parser.add_argument('-s', '--system', help='System prompt for chat mode')
    parser.add_argument('--status', action='store_true', help='Show server status')
    
    args = parser.parse_args()
    
    if not any([args.prompt, args.list, args.status]):
        parser.print_help()
        return
    
    ollama = OllamaCLI(args.host, args.port)
    
    if args.status:
        ollama.status()
    elif args.list:
        ollama.list_models()
    elif args.prompt:
        if args.chat:
            ollama.chat(args.model, args.prompt, args.system)
        else:
            ollama.generate(args.model, args.prompt)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()