---
name: universal-free-ai
description: >-
  Provides access to the Universal Free AI Model Hub running on the local PC.
  Allows querying top free models (Groq, Cerebras, SambaNova, OpenRouter Free,
  Gemini 2.0, Mistral Codestral, DeepSeek-R1, SiliconFlow, NVIDIA NIM) for
  ultra-fast code generation, multi-model council consensus, and code reviews.
---

# Universal Free AI Model Hub Skill

This skill guides the agent on how to leverage the zero-cost Free AI Model Hub integrated via MCP and the local Python runtime.

## Key Capabilities

1. **AI Council Mode (`free_ai_council`)**:
   - Dispatches a complex architecture or algorithm problem across 2–3 distinct LLMs simultaneously (e.g. DeepSeek-R1 + Llama-3.3-70B + Qwen-2.5-72B).
   - Combines their perspectives into a single unified consensus.

2. **Ultra-Fast Generation (`free_ai_query` with `category: "fast"`)**:
   - Routes through Groq or Cerebras (~500 tokens/second) for immediate boilerplate, tests, or regex creation.

3. **Deep Reasoning (`free_ai_query` with `category: "reasoning"`)**:
   - Routes through DeepSeek-R1, SambaNova Qwen 2.5 72B, or NVIDIA NIM for deep mathematical and logical derivations.

4. **Specialized Code Review (`free_ai_code_review`)**:
   - Uses Codestral, DeepSeek, or Qwen Coder to run structured security, performance, and bug audits.

## Model Catalog & Specialty Reference

| Provider | Top Free Model | Ideal For |
| :--- | :--- | :--- |
| **Groq** | `openai/gpt-oss-120b` | Ultra-fast code generation, transformations, summaries |
| **OpenRouter** | `nvidia/nemotron-3.5-lightning:free` | Free multi-model ecosystem & reasoning |
| **Mistral** | `codestral-latest` | Clean code reviews and refactoring |
| **Gemini** | `gemini-2.5-flash` | Multimodal, large 1M token context windows |
| **SambaNova** | `DeepSeek-V3.2` | High concurrency deep reasoning |
| **Cerebras** | `qwen-3.8-27b` | Wafer-scale ultra-low latency speed |

## Local CLI Reference

You can also run benchmarks or direct CLI queries at any time:
```powershell
$env:PYTHONPATH = '.agents'
python -m free_ai_hub.cli status
python -m free_ai_hub.cli benchmark
python -m free_ai_hub.cli query "Explain quicksort" --category fast
python -m free_ai_hub.cli council "Compare SQLite vs DuckDB for time series analytics"
```
