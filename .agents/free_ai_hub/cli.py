import sys
import asyncio
import argparse
from typing import Optional

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from .config import load_config
from .client import FreeAIClient
from .council import AICouncil
from .providers import PROVIDER_REGISTRY

async def cmd_status():
    config = load_config(reload=True)
    summary = config.get_status_summary()
    
    print("\n=======================================================")
    print("       UNIVERSAL FREE AI MODEL HUB - STATUS            ")
    print("=======================================================")
    print(f"Total Supported Providers : {summary['total_providers']}")
    print(f"Active Configured Keys    : {summary['active_count']}/{summary['total_providers']}\n")

    print("[+] ACTIVE PROVIDERS (Ready to use):")
    if not summary["active_providers"]:
        print("   (None configured yet - edit 'free_ai_keys.env' to add free keys)")
    else:
        for p in summary["active_providers"]:
            print(f"   * {p['display_name']} -> Default Model: {p['default_model']}")

    print("\n[-] INACTIVE PROVIDERS (Free keys available):")
    for p in summary["inactive_providers"]:
        print(f"   * {p['display_name']} ({p['env_key']})")
        print(f"     Signup Link: {p['doc_url']}")
        print(f"     Free Tier  : {p['free_tier_info']}")
    print("=======================================================\n")

async def cmd_benchmark():
    client = FreeAIClient()
    config = client.config
    active = config.get_active_providers()

    if not active:
        print("[!] No active providers found. Please add API keys to 'free_ai_keys.env' or '.env'.")
        return

    print(f"\n[+] Running Benchmark across {len(active)} active provider(s)...")
    tasks = [client.benchmark_provider(p.name) for p in active]
    results = await asyncio.gather(*tasks)

    for r in results:
        if r.get("status") == "online":
            print(f"  [ONLINE]  {r['display_name']:<30} | Model: {r['model']} | Latency: {r['latency_ms']:.1f}ms")
        else:
            print(f"  [ERROR]   {r['display_name']:<30} | Error: {r.get('error', 'Unknown')}")
    print()

async def cmd_query(prompt: str, category: str = "general", provider: Optional[str] = None, model: Optional[str] = None):
    client = FreeAIClient()
    print(f"\n[+] Querying Free AI Hub (Category: {category}, Provider: {provider or 'auto-failover'})...\n")
    try:
        res = await client.query(
            prompt=prompt,
            category=category,
            provider=provider,
            model=model
        )
        print(f"------------------- [{res.provider.upper()} - {res.model} ({res.latency_ms:.1f}ms)] -------------------")
        print(res.text.strip())
        print("-----------------------------------------------------------------------------------\n")
    except Exception as e:
        print(f"[!] Query Error: {e}\n")

async def cmd_council(question: str):
    council = AICouncil()
    print(f"\n[+] Convening AI Council on: \"{question}\"...\n")
    try:
        res = await council.debate(question=question)
        print("=======================================================")
        print("                 AI COUNCIL SYNTHESIS                  ")
        print("=======================================================")
        print(res.get("synthesis", ""))
        print("\n=======================================================")
        print("             INDIVIDUAL MODEL OPINIONS                 ")
        print("=======================================================")
        for op in res.get("council_opinions", []):
            if op.get("status") == "failed":
                print(f"\n--- {op['display_name']} (Failed) ---\nError: {op.get('error')}")
            else:
                print(f"\n--- {op['display_name']} ({op.get('model')} - {op.get('latency_ms', 0):.0f}ms) ---")
                print(op.get("response", "").strip())
        print("=======================================================\n")
    except Exception as e:
        print(f"[!] Council Error: {e}\n")

def main():
    parser = argparse.ArgumentParser(description="Universal Free AI Model Hub CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("status", help="Check active keys and provider status")
    subparsers.add_parser("benchmark", help="Test live connection and latency of active providers")

    query_parser = subparsers.add_parser("query", help="Query a free AI model")
    query_parser.add_argument("prompt", type=str, help="Prompt text")
    query_parser.add_argument("--category", choices=["general", "fast", "reasoning", "coding"], default="general")
    query_parser.add_argument("--provider", type=str, default=None)
    query_parser.add_argument("--model", type=str, default=None)

    council_parser = subparsers.add_parser("council", help="Debate question across multiple AI models")
    council_parser.add_argument("question", type=str, help="Question for the council")

    args = parser.parse_args()

    if args.command == "status" or args.command is None:
        asyncio.run(cmd_status())
    elif args.command == "benchmark":
        asyncio.run(cmd_benchmark())
    elif args.command == "query":
        asyncio.run(cmd_query(args.prompt, args.category, args.provider, args.model))
    elif args.command == "council":
        asyncio.run(cmd_council(args.question))

if __name__ == "__main__":
    main()
