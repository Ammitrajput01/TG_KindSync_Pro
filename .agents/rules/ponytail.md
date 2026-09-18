# 🦹‍♂️ Ponytail Ruleset — "The Lazy Senior Dev" Protocol

## Core Philosophy
> **"The best code is the code you never wrote."**  
> Every line of code added is a line that must be parsed, debugged, maintained, and loaded into context tokens. Do not write code to look productive; write minimal code to solve the exact problem.

---

## 🪜 The Laziness Ladder
Before writing ANY code, evaluating ANY task, or modifying ANY file, climb down the Laziness Ladder and **stop at the first rung that works**:

1. **Does this need to exist at all? (YAGNI)**
   - If the feature, abstraction, or helper isn't strictly requested or essential for correct execution right now, **do not write it**.
   - Resist speculative architecture: No future-proofing, no generic handlers for things that happen only once.

2. **Is it already in the codebase?**
   - Check existing utilities, helpers, and modules before writing a new function. Reuse verbatim.

3. **Can the standard library do it natively?**
   - Python: Use `pathlib`, `itertools`, `collections`, `functools`, `dataclasses`, `sqlite3`, `json`, `urllib.request`.
   - Node/Browser: Use native `fetch`, `URL`, `FormData`, modern Array methods, CSS grid/flexbox, `:has()`, native dialogs.
   - Do not pull or suggest third-party packages when standard built-ins take 2-3 lines.

4. **Is there a native platform/OS feature?**
   - Use native OS commands, PowerShell/Bash pipes, environment variables, and filesystem semantics rather than writing 50-line custom scripts.

5. **Can an existing dependency handle it?**
   - If a library is already imported in `requirements.txt` or `package.json`, use its built-in APIs rather than wrapping it in a custom layer.

6. **Only then, write the absolute minimum code required.**
   - Simple functions > complex classes.
   - 5-line inline logic > 40-line abstract class hierarchy with factories and singletons.
   - Clear variable names > 10 lines of obvious docstrings explaining the obvious.

---

## 🚫 Hard "Anti-Bloat" Rules
* **No Premature Abstraction**: Never create an interface or abstract base class until there are at least 3 distinct concrete implementations that need it.
* **No Redundant Comments**: Do not write comments like `# import os` or `# set user to active`. Code should be self-documenting.
* **Surgical Edits**: When editing existing code, touch only the lines necessary. Do not reformat surrounding code unless explicitly instructed.
* **Delete Over Add**: Whenever refactoring or upgrading, actively look for obsolete code, dead branches, and redundant variables to delete.
