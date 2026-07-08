# Module-Level Docstring — Real-World Example

This reference shows the exact docstring format from
`src/01_format_and_update_ids.py` in this workspace. When writing a new
script, replace the content fields but keep the section structure intact.

---

## Standalone Script Example

```python
"""
Format Hayles 2013 Phenotype Data and Update Gene Systematic IDs
=================================================================

Two-phase pipeline that (1) cleans and normalises the raw Hayles 2013
supplementary table, and (2) maps all gene systematic IDs against a
current PomBase annotation to correct identifiers changed by genome
annotation updates since 2013.

Phase 1 — Data Formatting
  - Strips whitespace from Systematic ID, phenotype description,
    classification, and dispensability columns
  - Normalises temperature notation: coerces variants such as
    "25, 32", "25 32", "32, 25" to the canonical "25,32"
  - Drops spurious columns (e.g. 'Unnamed: 12')
  - Prints summary statistics of phenotypic classification and
    gene dispensability categories

Phase 2 — Gene ID Mapping
  - Loads the PomBase gene annotation (gene_IDs_names_products.tsv)
  - Builds lookup tables from current systematic IDs, gene names,
    and synonyms (restricted to protein-coding genes by default)
  - Maps each input identifier through three layers:
      1. Direct systematic ID match
      2. Gene name → systematic ID lookup
      3. Synonym → systematic ID lookup
  - Identifies genes reclassified as pseudogene or ncRNA
  - Looks up current gene names for all entries

This script supersedes the original ``format_phenotype_input.py``
(which only performed Phase 1).

Input
-----
- ``data/raw/rsob130053supp2.xlsx``
  Hayles 2013 supplementary table (12 columns, 4,843 rows).
  Required columns: 'Systematic ID', 'Gene name'.

- PomBase annotation TSV (downloaded by 00_download_pombase_annotation.py)
  File: ``data/references/pombase-{release}_gene_IDs_names_products.tsv``

Output
------
- ``data/1_formatted/Hayles_2013_OB_formatted_phenotypes.xlsx``
  Cleaned phenotype data with updated Systematic ID and Gene name
  columns (12 columns, 4,843 rows).

- ``data/1_formatted/gene_id_mapping_changelog.xlsx``
  Change log with columns: original_systematic_id, original_gene_name,
  updated_systematic_id, updated_gene_name, note, update_type.

Usage
-----
    mamba run -n bioinformatics python src/01_format_and_update_ids.py
    mamba run -n bioinformatics python src/01_format_and_update_ids.py --verbose
    mamba run -n bioinformatics python src/01_format_and_update_ids.py \\
        --gene-filter "gene_type != 'pseudogene'"

Author:   Yusheng Yang (guidance) + Hermes (implementation)
Date:     2026-06-08
Version:  1.0.0
"""
```

---

## Library Module Example

For library modules (imported, not invoked from CLI), omit the Usage
block and the LOGGING/CONFIG/MAIN sections. Example from
`src/growth_signals.py`:

```python
"""
Growth Signal Definitions for S. pombe Phenotype Classification
===============================================================

Shared module defining growth-related keyword signals, their severity
tiers, and the ``classify_growth()`` engine that replaces the brittle
if-elif chains in the original categorize scripts.

Signals are detected independently from a phenotype description, then
resolved into a fine-grained ``Category`` label and a coarse
``Growth_tier`` (1–5) for downstream statistical analysis.

Input
-----
- A phenotype description string (e.g. from ``Deletion mutant phenotype
  description`` column in the Hayles table).

Output
------
- ``tuple[str, int]`` — (category_name, growth_tier).

Usage
-----
    from src.growth_signals import classify_growth

    cat, tier = classify_growth("ESSENTIAL germinated spores at 25,32")
    # cat == "germinated", tier == 2

Author:   Yusheng Yang (guidance) + Hermes (implementation)
Date:     2026-06-09
Version:  1.0.0
"""
```

---

## Section-by-Section Rules

| Section | Content | Required? |
|---|---|---|
| **Title** | One-liner, followed by `=====` underline matching title length | Always |
| **Description** | 1-3 paragraphs covering business logic, algorithm, context. Bullet lists OK for multi-step pipelines | Always |
| **Input** | What files/data the script reads, format expectations | Always for standalone scripts; optional for library modules |
| **Output** | What files the script writes, their column/row structure | Always for standalone scripts; optional for library modules |
| **Usage** | Copy-pasteable CLI commands (prefixed with `mamba run -n` or equivalent) | Standalone scripts only |
| **Author / Date / Version** | `Author: Name (guidance) + Agent (implementation)`, `Date: YYYY-MM-DD`, `Version: X.Y.Z` | Always |

## Language

When a project repository will be made public alongside a publication,
write all documentation — module docstrings, ``docs/*.md``, the project
``README.md`` — in **English**.
