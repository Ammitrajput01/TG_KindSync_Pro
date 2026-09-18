# Autonomous Free AI Multi-Model Orchestration Rule

## Purpose
The user has configured a local Universal Free AI Model Hub (Groq, OpenRouter, Mistral Codestral, Gemini 2.5 Flash, SambaNova, Cerebras) and explicitly requested that the agent autonomously leverage these models **WITHOUT requiring explicit prompts or manual triggers from the user**.

---

## Autonomous Activation Guidelines

### 1. Complex Code Changes & Bug Fixing (Mistral Codestral Audit)
- When writing non-trivial functions, refactoring modules, or fixing stubborn bugs:
  - Autonomously trigger a code review using Mistral Codestral via `free_ai_hub`:
    ```powershell
    python -m free_ai_hub.cli query --category coding "Review this snippet for edge cases: <code_or_logic>"
    ```
  - Incorporate Codestral's insights directly into the final code to ensure 100% bug-free delivery.

### 2. High-Volume Boilerplate & Fast Drafting (Groq LPU Acceleration)
- When generating repetitive data structures, large regexes, lookup tables, or benchmark scripts:
  - Autonomously leverage Groq for ultra-fast generation:
    ```powershell
    python -m free_ai_hub.cli query --category fast "<prompt>"
    ```

### 3. Architecture & Core Design Decisions (AI Council Mode)
- When deciding between major architectural approaches (e.g. asyncio vs threading, SQLite schema indexes, queue buffers, rate limit strategies):
  - Autonomously convene the AI Council to get multi-model consensus:
    ```powershell
    python -m free_ai_hub.cli council "<architectural question>"
    ```
  - Synthesize the Council's consensus to give the user the absolute best solution.

### 4. Continuous Model Health
- If any external call is needed, the `free_ai_hub` automatically handles fallback across Groq, OpenRouter, Mistral, and Gemini.
