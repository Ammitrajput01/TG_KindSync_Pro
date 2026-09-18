---
name: graphify
description: "AST Codebase Knowledge Graph skill. Instantly map repository structure, classes, methods, and functions without burning LLM context tokens. Run 'python .agents/tools/graphify.py build' or 'query <symbol>'."
---

# 🌲 Graphify — AST Codebase Knowledge Graph Skill

## Purpose
Graphify turns the codebase into a queryable AST index. Instead of opening entire source files or performing blind greps across thousands of lines, use Graphify to find exact symbol locations, method arguments, and class hierarchies in milliseconds.

## Quick Commands
```bash
# 1. Build or refresh the graph
python .agents/tools/graphify.py build --dir .

# 2. Query any symbol (Class, Function, Method)
python .agents/tools/graphify.py query "SymbolName"
```

## When to Use
- When locating where a specific function, class, or method is implemented.
- When inspecting class inheritance or signatures without reading 500 lines of file contents.
- Before refactoring to understand symbol definitions across modules.
