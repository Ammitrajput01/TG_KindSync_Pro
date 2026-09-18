"""
🌲 Graphify — AST Codebase Knowledge Graph Generator
Builds a fast, zero-token structural map of codebase symbols, classes, functions, and imports.
Enables instant symbol querying without dumping entire files into LLM context.
"""

import os
import sys
import ast
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

IGNORE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules", ".gemini", 
    "dist", "build", "export_backups", "db_backups", "member_backups"
}

def analyze_python_file(filepath: Path) -> Dict[str, Any]:
    try:
        source = filepath.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(filepath))
    except Exception as e:
        return {"error": str(e)}

    classes = {}
    functions = {}
    imports = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = [arg.arg for arg in item.args.args]
                    methods.append({
                        "name": item.name,
                        "line": item.lineno,
                        "args": args,
                        "is_async": isinstance(item, ast.AsyncFunctionDef)
                    })
            classes[node.name] = {
                "line": node.lineno,
                "methods": methods,
                "bases": [ast.unparse(b) for b in node.bases if hasattr(ast, 'unparse')]
            }
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [arg.arg for arg in node.args.args]
            functions[node.name] = {
                "line": node.lineno,
                "args": args,
                "is_async": isinstance(node, ast.AsyncFunctionDef)
            }
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                imports.append(f"{mod}.{alias.name}")

    return {
        "classes": classes,
        "functions": functions,
        "imports": imports,
        "line_count": len(source.splitlines())
    }

def build_graph(root_dir: Path) -> Dict[str, Any]:
    graph = {
        "root": str(root_dir),
        "files": {},
        "symbols_index": {}
    }

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            if filename.endswith(".py"):
                fpath = Path(dirpath) / filename
                rel_path = str(fpath.relative_to(root_dir)).replace("\\", "/")
                file_info = analyze_python_file(fpath)
                if "error" not in file_info:
                    graph["files"][rel_path] = file_info
                    
                    # Populate symbol index
                    for cls_name, cls_meta in file_info["classes"].items():
                        graph["symbols_index"][cls_name] = {
                            "type": "class",
                            "file": rel_path,
                            "line": cls_meta["line"],
                            "methods": [m["name"] for m in cls_meta["methods"]]
                        }
                        for m in cls_meta["methods"]:
                            graph["symbols_index"][f"{cls_name}.{m['name']}"] = {
                                "type": "method",
                                "file": rel_path,
                                "line": m["line"],
                                "args": m["args"]
                            }
                    for fn_name, fn_meta in file_info["functions"].items():
                        graph["symbols_index"][fn_name] = {
                            "type": "function",
                            "file": rel_path,
                            "line": fn_meta["line"],
                            "args": fn_meta["args"]
                        }

    return graph

def main():
    parser = argparse.ArgumentParser(description="Graphify Codebase Knowledge Graph")
    subparsers = parser.add_subparsers(dest="command")

    build_p = subparsers.add_parser("build", help="Build codebase AST graph")
    build_p.add_argument("--dir", default=".", help="Root directory")
    build_p.add_argument("--output", default="codebase_graph.json", help="Output JSON path")

    query_p = subparsers.add_parser("query", help="Query symbol in graph")
    query_p.add_argument("symbol", help="Symbol name (class or function)")
    query_p.add_argument("--graph", default="codebase_graph.json", help="Graph file path")

    args = parser.parse_args()

    if args.command == "build" or not args.command:
        root = Path(getattr(args, "dir", "."))
        out_path = Path(getattr(args, "output", "codebase_graph.json"))
        graph = build_graph(root)
        out_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
        print(f"✅ Graphify built: {len(graph['files'])} files parsed, {len(graph['symbols_index'])} symbols indexed -> {out_path}")

    elif args.command == "query":
        graph_path = Path(args.graph)
        if not graph_path.exists():
            print("❌ codebase_graph.json not found. Run 'build' first.")
            return
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        sym = args.symbol
        matches = {k: v for k, v in graph.get("symbols_index", {}).items() if sym.lower() in k.lower()}
        if matches:
            print(f"🎯 Found {len(matches)} match(es) for '{sym}':")
            for k, v in list(matches.items())[:15]:
                print(f"  - {k} ({v['type']}): {v['file']}:{v['line']}")
        else:
            print(f"❌ No symbol matching '{sym}' found.")

if __name__ == "__main__":
    main()
