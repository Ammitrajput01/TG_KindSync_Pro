# ⚡ RTK & Token Killer Terminal Output Protocol

## Goal
Minimize agent context consumption by eliminating terminal noise, progress bars, ANSI escape codes, and redundant logs while preserving 100% of crucial error traces and state information.

---

## Rules for Command Execution & Output Processing

1. **Avoid Dumping Massive Verbose Outputs**:
   - Limit outputs from commands known to generate thousands of lines:
     - `git log -n 5 --oneline` instead of `git log`
     - Targeted tests: `pytest tests/test_target.py -q` instead of running full suites with debug logs unless requested.
     - Use `head` or `Select-Object -First 20` or `-Last 20` when inspecting large log files.

2. **Strip Terminal Decoration**:
   - Terminal color sequences (`\x1b[...]`), spinners, carriage returns (`\r`), and dynamic percentage bars burn LLM tokens without providing value. Strip them before processing.

3. **Use `.agents/tools/token_compressor.py`**:
   - For filtering huge test results or system outputs, route through the token compressor tool:
     ```bash
     python .agents/tools/token_compressor.py --input <log_file>
     ```
   - Retains: Exit code, failure locations, tracebacks, and execution summaries.
   - Strips: Passing test dots, download progress lines, decorative box-drawing lines, duplicate blank lines.
