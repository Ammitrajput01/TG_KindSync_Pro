"""
⚡ Token Compressor & RTK Clean-Output Engine
Filters noisy terminal logs, build traces, and test outputs to save 60-90% LLM tokens.
"""

import sys
import re
import argparse
from pathlib import Path

# ANSI escape sequence regex
ANSI_REGEX = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
PROGRESS_BAR_REGEX = re.compile(r'(\[\s*[#=\-\.]+\s*\]|\d+%\s*\|\s*[\#=\-\.]+|\r)')

def strip_ansi(text: str) -> str:
    return ANSI_REGEX.sub('', text)

def compress_output(raw_text: str, max_lines: int = 200) -> str:
    # 1. Strip ANSI escape sequences
    clean = strip_ansi(raw_text)
    
    # 2. Normalize carriage returns (spinners/progress bars)
    lines = []
    for raw_line in clean.splitlines():
        # If line contains \r, keep only final update
        if '\r' in raw_line:
            parts = [p.strip() for p in raw_line.split('\r') if p.strip()]
            line = parts[-1] if parts else ''
        else:
            line = raw_line.rstrip()
            
        # Strip progress bar noise
        if PROGRESS_BAR_REGEX.search(line) and len(line) < 120 and ('ETA' in line or '%' in line):
            continue
            
        lines.append(line)
        
    # 3. Collapse multiple blank lines
    collapsed = []
    last_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank:
            if not last_blank:
                collapsed.append('')
            last_blank = True
        else:
            collapsed.append(line)
            last_blank = False
            
    # 4. Truncate if exceeds max_lines while preserving head + tail (failures/summary)
    if len(collapsed) > max_lines:
        head_count = max_lines // 3
        tail_count = max_lines - head_count - 1
        omitted = len(collapsed) - head_count - tail_count
        result = collapsed[:head_count] + [f"\n... [⚡ RTK: {omitted} intermediate lines compressed to save tokens] ...\n"] + collapsed[-tail_count:]
        return '\n'.join(result)
        
    return '\n'.join(collapsed)

def main():
    parser = argparse.ArgumentParser(description="Compress terminal logs to save LLM tokens")
    parser.add_argument("--input", "-i", type=str, help="Path to input log file (reads stdin if omitted)")
    parser.add_argument("--max-lines", "-m", type=int, default=250, help="Maximum lines to retain")
    args = parser.parse_args()

    if args.input:
        content = Path(args.input).read_text(encoding="utf-8", errors="ignore")
    else:
        content = sys.stdin.read()

    compressed = compress_output(content, max_lines=args.max_lines)
    print(compressed)

if __name__ == "__main__":
    main()
