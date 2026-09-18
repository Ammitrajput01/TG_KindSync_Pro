"""
Model Context Protocol (MCP) Server for Universal Free AI Hub.
Communicates via stdio JSON-RPC 2.0 with Antigravity and other MCP-compliant hosts.
"""

import sys
import json
import asyncio
import traceback
from typing import Dict, Any, List, Optional

from .config import load_config
from .client import FreeAIClient
from .council import AICouncil
from .providers import PROVIDER_REGISTRY

# Available MCP Tool Definitions
TOOLS_MANIFEST = [
    {
        "name": "free_ai_query",
        "description": "Query any free AI model (Groq, Cerebras, SambaNova, OpenRouter Free, Gemini, Mistral, SiliconFlow, DeepSeek, HuggingFace) with automatic failover and smart routing.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The prompt / instruction to send to the free AI model."
                },
                "category": {
                    "type": "string",
                    "enum": ["general", "fast", "reasoning", "coding"],
                    "default": "general",
                    "description": "Category for smart auto-routing (fast = Groq/Cerebras, reasoning = DeepSeek/SambaNova, coding = Codestral/Qwen)."
                },
                "provider": {
                    "type": "string",
                    "description": "Optional specific provider (groq, cerebras, sambanova, openrouter, gemini, mistral, siliconflow, deepseek, nvidia)."
                },
                "model": {
                    "type": "string",
                    "description": "Optional specific model ID (e.g. llama-3.3-70b-versatile, deepseek/deepseek-r1:free, gemini-2.0-flash)."
                },
                "system_prompt": {
                    "type": "string",
                    "description": "Optional system prompt instructions."
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "free_ai_council",
        "description": "Consult the AI Council: runs prompt simultaneously across 2-3 distinct free models and returns synthesized consensus.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The challenging engineering or architectural problem for the council to debate."
                },
                "providers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of providers to participate in the council."
                }
            },
            "required": ["question"]
        }
    },
    {
        "name": "free_ai_code_review",
        "description": "Perform an ultra-fast, rigorous code review using free coding models (Codestral, DeepSeek, Qwen Coder, Llama 3.3).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The source code snippet to review."
                },
                "language": {
                    "type": "string",
                    "default": "python",
                    "description": "Programming language of the code snippet."
                },
                "focus": {
                    "type": "string",
                    "default": "bugs, performance, and security",
                    "description": "Specific focus area for the review."
                }
            },
            "required": ["code"]
        }
    },
    {
        "name": "free_ai_health_check",
        "description": "Check the live status of all configured free AI provider keys and measure response latencies.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]

class MCPServer:
    def __init__(self):
        self.config = load_config()
        self.client = FreeAIClient(config=self.config)
        self.council = AICouncil(client=self.client)

    async def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        self.config.reload()  # Reload in case user edited keys file

        if name == "free_ai_query":
            prompt = arguments.get("prompt", "")
            category = arguments.get("category", "general")
            provider = arguments.get("provider")
            model = arguments.get("model")
            system_prompt = arguments.get("system_prompt")
            
            res = await self.client.query(
                prompt=prompt,
                system_prompt=system_prompt,
                category=category,
                provider=provider,
                model=model
            )
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"[{res.provider.upper()} ({res.model}) - Latency: {round(res.latency_ms, 1)}ms]\n\n{res.text}"
                    }
                ]
            }

        elif name == "free_ai_council":
            question = arguments.get("question", "")
            providers = arguments.get("providers")
            council_res = await self.council.debate(question=question, providers=providers)
            
            output = f"# AI Council Consensus\n\n**Question**: {question}\n\n"
            output += f"## Synthesized Consensus\n{council_res.get('synthesis', '')}\n\n"
            output += "## Individual Member Perspectives\n"
            for op in council_res.get("council_opinions", []):
                if op.get("status") == "failed":
                    output += f"### {op['display_name']} (Failed)\nError: {op.get('error')}\n\n"
                else:
                    output += f"### {op['display_name']} ({op.get('model')} - {round(op.get('latency_ms', 0))}ms)\n{op.get('response')}\n\n"

            return {
                "content": [
                    {
                        "type": "text",
                        "text": output
                    }
                ]
            }

        elif name == "free_ai_code_review":
            code = arguments.get("code", "")
            language = arguments.get("language", "python")
            focus = arguments.get("focus", "bugs, performance, and security")
            
            prompt = (
                f"Please perform a deep, actionable code review for the following {language} code.\n"
                f"Focus on: {focus}.\n\n"
                f"```{language}\n{code}\n```\n\n"
                f"Structure your feedback:\n"
                f"1. Critical Bugs / Edge Cases\n"
                f"2. Performance & Memory Optimizations\n"
                f"3. Cleanliness & Best Practices\n"
                f"4. Refactored Code Snippet (if applicable)"
            )
            
            res = await self.client.query(
                prompt=prompt,
                category="coding",
                system_prompt="You are an elite Senior Principal Software Architect specializing in code reviews."
            )
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"[Review by {res.provider.upper()} ({res.model})]\n\n{res.text}"
                    }
                ]
            }

        elif name == "free_ai_health_check":
            summary = self.config.get_status_summary()
            tasks = []
            for prov in self.config.get_active_providers():
                tasks.append(self.client.benchmark_provider(prov.name))
            
            benchmark_results = await asyncio.gather(*tasks, return_exceptions=True) if tasks else []
            
            report = f"# Universal Free AI Model Hub Status\n\n"
            report += f"- Active Providers Configured: **{summary['active_count']}/{summary['total_providers']}**\n\n"
            
            report += "## Active Providers Health & Latency:\n"
            if not benchmark_results:
                report += "_No active keys found. Add keys in `free_ai_keys.env` to activate providers._\n"
            else:
                for b in benchmark_results:
                    if isinstance(b, dict):
                        status_icon = "✅" if b.get("status") == "online" else "❌"
                        report += f"- {status_icon} **{b.get('display_name', b.get('provider'))}**: "
                        if b.get("status") == "online":
                            report += f"Online ({b.get('model')}) - Latency: `{round(b.get('latency_ms', 0), 1)}ms`\n"
                        else:
                            report += f"Error: {b.get('error', 'Unknown')}\n"

            report += "\n## Available Providers Catalog:\n"
            for p in summary["inactive_providers"]:
                report += f"- ⚪ **{p['display_name']}**: `{p['env_key']}` missing. [Get Free Key]({p['doc_url']}) — {p['free_tier_info']}\n"

            return {
                "content": [
                    {"type": "text", "text": report}
                ]
            }

        else:
            raise ValueError(f"Unknown tool: {name}")

    async def run_stdio(self):
        """Standard JSON-RPC 2.0 stdio event loop (Windows compatible)."""
        while True:
            line = await asyncio.to_thread(sys.stdin.readline)
            if not line:
                break
            
            text = line.strip()
            if not text:
                continue

            try:
                msg = json.loads(text)
            except Exception:
                continue

            msg_id = msg.get("id")
            method = msg.get("method")
            params = msg.get("params", {})

            # Standard MCP Handshake
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "universal-free-ai-hub",
                            "version": "1.0.0"
                        }
                    }
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            elif method == "notifications/initialized":
                pass

            elif method == "ping":
                response = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": TOOLS_MANIFEST
                    }
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                try:
                    result = await self.handle_tool_call(tool_name, arguments)
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": result
                    }
                except Exception as e:
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": {
                            "isError": True,
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Error executing {tool_name}: {str(e)}\n{traceback.format_exc()}"
                                }
                            ]
                        }
                    }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()

            else:
                if msg_id is not None:
                    response = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()

def main():
    server = MCPServer()
    try:
        asyncio.run(server.run_stdio())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
