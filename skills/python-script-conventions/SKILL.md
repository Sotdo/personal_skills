---
name: python-script-conventions
description: Use when generating, modifying, or reviewing Python scripts (3.12+). Specifies section layout, import ordering, type system, logging, dataclass patterns, and AI-agent-friendly design principles. Load this skill whenever creating or editing a .py file — especially for bioinformatics/data-science scripts.
version: 1.4.0
author: Yusheng Yang
license: MIT
metadata:
  hermes:
    tags: [python, conventions, style-guide, code-quality, ai-design]
    related_skills: [plan, writing-plans, test-driven-development, project-scaffolding, systematic-debugging]
---

# Python Script Conventions (Modern Python 3.12+)

## Overview

This skill defines the coding standards and design patterns to follow when generating or modifying Python scripts in this workspace. It codifies a consistent layout, modern Python 3.12+ idioms, and AI-agent-friendly design so that every script reads like it belongs to the same codebase.

The companion file `templates/agent_script_template.py` provides a concrete reference implementation of these principles. **Always open that template as a starting point when writing a new script from scratch.**

Apply these rules thoughtfully — if a rule would make a particular script worse, adapt accordingly.

---

## When to Use

- **Creating any new `.py` script** in this workspace — load this skill first, then open `templates/agent_script_template.py` as the starting structure.
- **Modifying an existing script** — refactor to match these conventions when the edit is substantial (layout, imports, logging, etc.).
- **Reviewing a PR or diff that includes Python files** — use the checklist below as review criteria.
- **Generating a single-file script** meant for `uv` or standalone execution.

### When NOT to Use

- Libraries or packages with multiple modules (those follow their own structure; this skill targets standalone scripts).
- Jupyter notebooks (use the jupyter-live-kernel skill instead).
- Code snippets in markdown docs (unless they're illustrative of the template).

### Modifying an Existing Script

When *modifying* a script that was written before this skill was applied (or
that partially follows it), **treat the edit as a section-layout review**:

1. Re-read the entire script's section structure before editing — don't just
   jump to the line you want to change.
2. If you're adding a new import, put it in the top-level IMPORTS section,
   **not** next to where it's used in the body. The skill's import ordering
   rules apply to modifications as much as to new files.
3. If the edit is substantial (10+ lines changed, new imports, new functions),
   refactor the file to match the full section layout. This repays quickly
   — the next edit benefits from the structure.
4. Run the verification checklist after the edit, not just before it.

---

### 1.1 Standalone Scripts vs Library Modules

A file in ``src/`` is either a **standalone script** (invoked from the
command line) or a **library module** (imported by other scripts). They
have different structures:

**Standalone script** — follows the full 7-section layout (IMPORTS →
DECORATORS → CONSTANTS → CONFIG → LOGGING → CORE → MAIN). Contains
``parse_args()`` + ``if __name__ == "__main__": sys.exit(main())``.

**Library module** — omits the LOGGING, CONFIG, and MAIN sections.
Contains only IMPORTS, CONSTANTS (including enums and dataclasses), and
CORE LOGIC. No ``parse_args()``, no ``main()``, no ``setup_logger()``.
The module-level docstring omits the CLI Usage block from the §3.2
format, but keeps the title, description, I/O spec, and metadata.

Check ``src/growth_signals.py`` in this workspace for a concrete example.

### 1.2 Script Structure & Layout

Scripts should follow this section order, reflecting a natural information **dependency hierarchy** — constants → data models → core logic → CLI → main — so each section only depends on what came before it. Omit sections that a script does not need (e.g., no enums, no decorators).

Always use the `agent_script_template.py` template as the starting point:

```python
# =============================================================================
# IMPORTS
# =============================================================================
...
# =============================================================================
# DECORATORS
# =============================================================================
...
# =============================================================================
# GLOBAL CONSTANTS & ENUMS
# =============================================================================
...
# =============================================================================
# CONFIGURATION & DATACLASSES
# =============================================================================
...
# =============================================================================
# LOGGING SETUP
# =============================================================================
...
# =============================================================================
# CORE LOGIC (FUNCTIONS / CLASSES)
# =============================================================================
...
# =============================================================================
# MAIN EXECUTION
# =============================================================================
...
```

### Imports Ordering

Group imports into three blocks, sorted alphabetically within each block:

```python
# 1. Standard Library Imports
import argparse
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

# 2. Data Processing Imports
import pandas as pd

# 3. Third-party Imports
from loguru import logger
```

### Entry Point

Always separate argument parsing into a dedicated `parse_args()` function, and guard execution with:

```python
if __name__ == "__main__":
    sys.exit(main())
```

Use `sys.exit(1)` on expected failures in `main()` so external orchestration tools can detect errors.

---

## 2. Modern Python 3.12+ Toolkit

### 2.1 Type System

- Use native `list` and `dict` (not `typing.List`, `typing.Dict`).
- Use `X | None` instead of `Optional[X]`.
- Create type aliases with the `type` keyword: `type GeneDict = dict[str, list[float]]`.
- Define generics with `def func[T](...)` rather than legacy `TypeVar`.
- Provide specific, domain-relevant types (`dict[str, GeneRecord]`) rather than bare `dict` or `Any`.

### 2.2 Data & Configuration

- Use `@dataclass(kw_only=True, slots=True, frozen=True)` for configuration objects. Keyword-only instantiation prevents positional-argument bugs; `frozen=True` guarantees immutability.
- When external data validation is needed, consider Pydantic.
- Use `enum.StrEnum` (Python 3.11+) for tightly grouped string markers like column names, operation modes, or categorical statuses. Do **not** use `StrEnum` for isolated singleton constants (a single API URL or regex pattern).

### 2.3 Control Flow

- Prefer structural pattern matching (`match...case`) over long `if-elif-else` chains when handling categorical logic or enum variants.
- Replace deeply nested `if-else` with guard clauses: handle failure, missing data, and edge cases at the top of the function and return or raise immediately, keeping the happy path at minimal indentation.

### 2.4 Logging & I/O

- Never use `print` for runtime output. Use `loguru`.
- With loguru, f-strings in log calls are fine (loguru handles lazy evaluation internally) — unlike stdlib `logging` where `%s` formatting is the convention for performance. Prefer f-strings for consistency with the rest of the codebase.
- Expose a `--verbose` CLI flag for debug-level logging.
- Apply `@logger.catch` on core functions to capture exceptions automatically rather than sprinkling `try/except` throughout.
- Use `pathlib.Path` for all path operations (`/` concatenation, `read_text()`, `write_text()`). Avoid `os.path`.

### 2.5 Dependencies

- Use PEP 723 `/// script` metadata blocks for single-file scripts so they can run via `uv` without external `requirements.txt`. Comment this out with `#` when not needed — it is optional.

---

## 3. Code Quality & Readability

### 3.1 F-Strings

- Use f-strings for all string interpolation. Avoid `.format()` and `%` formatting.
- Apply format specifiers for readability: `f"{value:.2f}"`, `f"{percent:.1%}"`, `f"{count:,}"`, `f"{name!r}"`.

### 3.2 Docstrings

Two levels of docstring with different conventions:

**Module-level docstring** (the ``"""..."""`` block at the very top of each
script) — acts as the script's "business card". Follow this structure:

```
"""
One-Liner Title
===============

[2–3 paragraphs: business logic, core algorithm, applicable context]

Input
-----
- What files does this script read? What columns / format does it expect?

Output
------
- What files does this script write? What is their structure?

Usage
-----
    command line example 1
    command line example 2

Author:   [Name] (guidance) + [AI Agent] (implementation)
Date:     YYYY-MM-DD
Version:  1.0.0
"""
```

**Documentation language.** When a project repository will be made public
(e.g. released alongside a publication), write all documentation —
module docstrings, ``docs/*.md``, the project ``README.md`` — in English.
This ensures the repo is immediately usable by an international audience
without a translation step.

**Function-level docstrings** — write a **single-line, concise summary**
for each function and class. Rely on **Type Hints** — not verbose
parameter blocks (``Parameters\n----------\n...\nReturns\n-------\n...``) —
to describe arguments and return values.

### 3.3 Change Documentation (Code Review Summaries)

When providing a summary of code changes, fixes, or refactors, use a
**three-column table** format — this is the user's explicit preference:

| Problem | Root Cause | Fix |
|---|---|---|
| What was wrong | Why it was a problem (what it caused, what would break) | What was changed, exactly |

Each row is one atomic concern. The "Root Cause" column must explain
**why** something is a problem, not just restate the problem:

```
| Column `One or multi basic phenotypes` had NaN for inconsistent genes | NaN propagates into downstream merge scripts where undefined values silence data quality checks and confuse anyone inspecting the spreadsheet | Fill NaN with explicit label `Temp_mismatch` and update the Excel sheet filter from `.isna()` to `== "Temp_mismatch"` |
```

### 3.4 Context Managers

- Use `with` when opening file handles directly (`Path.open()`, `open()`) or managing resources that implement `__enter__`/`__exit__` (`sqlite3.connect()`, `threading.Lock()`, `tempfile.TemporaryDirectory()`).
- Do **not** wrap higher-level library calls that manage their own resource lifecycle internally (e.g., `pd.read_csv(path)` or `df.to_csv(path)` — pandas handles file handles itself).

### 3.3b Column & Value Naming

When adding columns to a DataFrame or defining categorical values that
appear in tabular output:

- **Column names**: use `under_score` (snake_case), concise but unambiguous.
  A good column name is short enough to fit in a spreadsheet column header
  but descriptive enough that a partner reading the file doesn't need the
  docstring. Examples: `Consistency_25_32` (not `Consistency at temperatures`),
  `Phenotype_count` (not `One or multi basic phenotypes`).

- **Value labels**: use consistent noun‑style across all values in a column.
  Avoid mixing adjectives, prepositions, and nouns within the same column.
  Examples: `Single / Multiple / Temp_mismatch` (not `One phenotype / Multi
  phenotypes / Temperature inconsistent`), `Consistent / Only_32 / Mismatch`
  (not `Consistent / Only at 32 / Inconsistent`). This makes filtering,
  group‑by, and spreadsheet inspection far easier.

### 3.3c Output File Separation

When a script produces both main data output and derived inspection /
visualisation / diagnostic tables, separate them into **two files**:

- **Data output**: the canonical, re‑loadable dataset that downstream
  scripts consume. Contains only data sheets — no secondary pivot tables,
  formatted inspection tables, or diagnostic views.
- **Inspection output**: human‑review tables for validation. Contains
  cross‑tabulations, multi‑level pivots, conditional formatting, and
  any table whose primary purpose is quality control rather than data
  exchange.

Naming convention: let the data output determine the name, and derive
the inspection name by replacing a key word:
``Hayles_2013_OB_categorized_phenotypes.xlsx`` →
``Hayles_2013_OB_inspection_phenotypes.xlsx``.

### 3.4 Decorators

- Freely use standard library decorators: `@functools.cache`, `@contextlib.contextmanager`, `@staticmethod`, `@classmethod`, `@property`.
- Create custom decorators only when they eliminate repetitive boilerplate spanning 3+ functions. Do not create decorators for a single-use abstraction.
- Every custom decorator must use `@functools.wraps` to preserve the wrapped function's `__name__`, `__doc__`, and type hints.

### 3.5 Change Communication (for AI‑agent responses)

When summarising a code modification — a bug fix, a refactor, a feature
addition — present every meaningful change in a **three‑column table**:

| Column | Content |
|---|---|
| **What changed** | The specific file, symbol, or behaviour that was different from expected |
| **Why (problem + consequence)** | Explain WHY this was a problem — what would have happened if it weren't fixed (wrong result, crash, silent data loss, misclassification). **Do not** just restate the fix |
| **How (the fix)** | What was done to resolve it (the concrete transformation) |

This format applies when you fixed a bug, refactored code, identified an
inconsistency, or the user requests a summary of changes. For single
trivial edits (one‑line import fix, a constant rename) a sentence
suffices — use judgement.

---

## 4. AI-Agent Friendly Design

- **Pure Functions**: Minimize implicit global state. A function's output should depend only on its arguments. This lets AI agents test and refactor individual functions without reconstructing the entire script's state.
- **Single Responsibility**: Separate file I/O from business logic. Give each function one clear job so agents can reason about and compose them like building blocks.
- **Dependency Injection**: Pass configuration objects and strategies into function/class initializers rather than instantiating them internally. Flattened dependency trees are easier for agents to trace and debug.

---

## 5. Class Design

- **Data over Behavior**: Favor immutable dataclasses for holding state. Only define classes (with methods) when you genuinely need to manage stateful resources or shared lifecycle logic.
- **Avoid Deep Inheritance**: Prefer composition and flat structures over multi-level class hierarchies.

---

## Workflow: Creating a Python Script

1. **Load this skill** — `skill_view(name='python-script-conventions')` to re-read the rules.
2. **Open the template** — `skill_view(name='python-script-conventions', file_path='templates/agent_script_template.py')` to get the starting structure.
3. **Write the module-level docstring** — replace the template's example with
   the script's actual one-liner title, description, I/O specification, CLI
   usage examples, and metadata (see §3.2 for the full format).
4. **Customize sections** — replace the imports, enums, dataclasses, core logic, and CLI args with the script's actual requirements.
5. **Add PEP 723 metadata** at the top if the script has dependencies meant to run standalone via `uv`.
6. **Verify** against the checklist below.

---

## Common Pitfalls

0. **Pipeline-renumbering patch survivability.** When `mv`-renaming numbered pipeline scripts to a new sequence (e.g. `02_* → 03_*`), all earlier `patch` operations on those files survive the rename only if the editor persisted the patches before the `mv`. If a context boundary or tool restart occurred between the patch and the rename, the old content may have reappeared. **Always verify after renumbering:**
   - Shared constants (`MODIFIER_WORDS`, `GROWTH_KEYWORDS`, `DEFAULT_INPUT`, `DEFAULT_OUTPUT`) match what you believe they should be.
   - Logic patches (`classify_one_phenotype()` comma‑prefix fix, etc.) survived.
   - Input / output data‑directory paths (`data/3_*` instead of stale `data/2_*`) are correct.
   The fast check: `grep -A4 "MODIFIER_WORDS = (" src/*_group_genes.py` + `grep -rn "data/[0-9]_" src/*.py`.

1. **Using `print()` instead of `loguru`.** The template already imports and sets up `loguru` — always use `logger.info()`, `logger.warning()`, `logger.debug()`, etc. `print()` slips through when the agent copy-pastes from quick experiments. The `--verbose` CLI flag is already built into the template pattern.

2. **Forgetting `frozen=True` on the `@dataclass` config.** If a config object represents parameters that are set once at startup and never modified, it MUST be frozen. Only omit `frozen` if the application explicitly requires hot-reloading or runtime mutation of the config.

3. **Missing `sys.exit(1)` on expected failures.** Return `1` from `main()` on expected failure paths so CI pipelines and shell scripts that check `$?` can detect errors. The template already does this — just remember to return non-zero from `main()` on failure branches.

4. **Using `os.path.join()` / `os.path.exists()` instead of `pathlib.Path`.** The template imports `Path` and uses it throughout. Keep that consistent — `pathlib` is more readable, composable, and less error-prone.

5. **Hardcoded string markers instead of `StrEnum`.** When the script uses column names, operation modes, or categorical statuses that appear in multiple places, define them as a `StrEnum`. This prevents silent breakage when a string changes in one place but not another.

6. **Creating decorators for single-use abstractions.** A decorator with only one consumer adds indirection without benefit. The rule: only create a custom decorator when it eliminates repetitive boilerplate across **3+** functions.

7. **Deep `if-elif-else` chains for categorical logic.** Two alternatives depending on the problem:

   - **Fixed enum variants** (the category set is known and closed): use
     `match...case` instead of a chain. It's more readable and the type
     checker can help ensure exhaustiveness.

   - **Rule-based classification from free-text** (keywords in a
     description drive the category): use the **signal-based
     classification** pattern instead. See `references/signal-based-classification.md`
     under this skill for the full recipe. Pay special attention to
     **contextual signal suppression** — a keyword within a compound
     phrase (e.g. "spores" in "germinated spores") may not be an
     independent signal.

   - **Keyword‑profile / vocabulary analysis** (counting and categorising
     every word across category groups): use **stem‑prefix matching** —
     short canonical stems with an exact‑match fallback, plus hyphenated
     phrase pre‑tokenisation. See `references/stem-prefix-classification.md`
     under this skill.

8. **Unused imports left after refactoring.** Imports that were added during development but became unused after the code was refactored are easy to miss — the linter only catches them if a type checker like Pyright or `ruff check` is configured. Before finalising a script, scan the import block and verify every symbol is actually referenced in the body. The checklist below catches this; the pitfall section reminds you to look for it even when no linter is active.

9. **Writing multi-line docstrings with formal Parameters/Returns blocks.** Section 3.2 mandates single-line docstrings — type hints carry the type information. When a core function has complex arguments, the natural instinct is to write NumPy-style or Sphinx-style docstrings with `Parameters\n----------\n...\nReturns\n-------\n...`. This violates the rule. The fix: keep the docstring to one concise line and let the type annotations do the rest. If the function genuinely needs narrative context, put it in a comment block inside the function body rather than in the docstring. This is the most commonly-violated rule because "important" functions feel like they deserve more documentation — resist the urge.

10. **Adding a new import inside a function body, class definition, or section header instead of the top-level IMPORTS section.** This happens most often when *patching* an existing script — the natural instinct is to add the import next to where the new code goes. Every import must live in the IMPORTS block at file scope. Imports placed elsewhere confuse the section structure, bypass the linting pass, and make the next editor hunt for where a symbol is imported. Fix: before applying a patch that needs a new import, scroll to the IMPORTS block, add it in the correct group, then reference it in the body.

11. **Forgetting to re-check `classify_phenotype_count()` logic after expanding MODIFIER_WORDS / GROWTH_KEYWORDS.** When adding words to the modifier or growth keyword lists, fewer commas will be classified as parallel (Multiple → Single shift). After any expansion, re-run the full pipeline and verify the count deltas are expected and justified. Verify with `df["Phenotype_count"].value_counts()` in the merged output.

---

## Verification Checklist

- [ ] Sections follow the ordered layout (IMPORTS → DECORATORS → CONSTANTS → CONFIG → LOGGING → CORE → MAIN)
- [ ] Imports grouped: standard library → data processing → third-party, sorted alphabetically within each group
- [ ] All imports are in the top-level IMPORTS section — none in function bodies, class definitions, or section headers
- [ ] No unused imports — every imported module/name is referenced in the script body
- [ ] No `print()` calls — all runtime output uses `loguru`
- [ ] `pathlib.Path` used everywhere (no `os.path`)
- [ ] F-strings for interpolation (no `.format()` or `%`)
- [ ] `@dataclass(kw_only=True, slots=True, frozen=True)` for configuration objects
- [ ] `StrEnum` for grouped string markers, not for singleton constants
- [ ] Guard clauses for edge cases at function top
- [ ] Library modules (imported, not run directly) omit LOGGING, CONFIG, MAIN sections — no `parse_args()`, no `main()`, no `setup_logger()`
- [ ] `parse_args()` function + `if __name__ == "__main__": sys.exit(main())` guard
- [ ] Module-level docstring follows the §3.2 format (title → description → Input → Output → Usage → metadata)
- [ ] Change documentation uses three-column table (Problem → Root Cause → Fix) when summarising code modifications
- [ ] Single-line docstrings on functions and classes
- [ ] `@logger.catch` on core logic functions
- [ ] `--verbose` CLI flag for debug-level logging
- [ ] No deep `if-elif-else` chains — use `match...case` for categorical branches
