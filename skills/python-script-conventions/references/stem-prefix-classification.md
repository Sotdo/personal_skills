# Stem-Prefix Text Classification for Keyword Profiles

## When to Use This Pattern

You have a collection of phenotype descriptions (or any semi-structured
biological text) and want to classify every word into a semantic category
— growth signal, morphology, viability, modifier, stop word, etc. — for
quality‑inspection purposes.

## Core Idea: Exact + Stem Matching

Word classification uses a **two-tier** approach:

1. **Exact match** in a hand-curated category set (handles compound /
   hyphenated tokens like ``small-colonies``, ``t-shaped``).
2. **Stem-prefix fallback** using short canonical stems (handles plurals
   and verb inflections without listing every form).

Example: the stem ``slight`` matches both ``slight``, ``slightly``,
and the data typo ``slightlylarger``. The stem ``division`` matches
``division``, ``divisions``. The stem ``diploid`` matches ``diploid``,
``diploids``, ``diploidising``, ``diploidises``.

## Implementation Pattern

```python
# 1. Define exact‑match sets for each category
MORPHOLOGY_WORDS = {"long", "curved", "septated", "rounded", …}
MOD_FREQ_WORDS  = {"occasionally", "often", "sometimes", …}
#   — Split modifiers into subcategories: Frequency / Degree / Quantity
MOD_FREQ_WORDS  = {"occasionally", "often", "sometimes", …}
MOD_DEGREE_WORDS = {"slightly", "very", "barely", "weak", …}
MOD_QUANT_WORDS  = {"some", "many", "once", "twice", …}

# 2. Define short stems (≥3 chars) for prefix matching
MORPH_STEMS     = {"long", "curv", "sept", "round", "larg", "centr", "chain", …}
MOD_FREQ_STEMS  = {"occasion", "often", "sometimes", "initial", "rapid", "possibl", …}
MOD_DEGREE_STEMS = {"slight", "very", "barely", "weak", …}
MOD_QUANT_STEMS  = {"some", "many", "once", "twice", "multi", …}

def classify(word: str) -> str:
    # Tier 1: exact match (handles compound / hyphenated tokens)
    if word in MORPHOLOGY_WORDS:
        return "Morphology"
    if word in MOD_FREQ_WORDS:
        return "Modifier:Frequency"
    if word in MOD_DEGREE_WORDS:
        return "Modifier:Degree"
    if word in MOD_QUANT_WORDS:
        return "Modifier:Quantity"
    …

    # Tier 2: stem‑prefix fallback
    for stem in MORPH_STEMS:
        if word.startswith(stem) and len(stem) >= 3:
            return "Morphology"
    for stem in MOD_FREQ_STEMS:
        if word.startswith(stem) and len(stem) >= 3:
            return "Modifier:Frequency"
    for stem in MOD_DEGREE_STEMS:
        if word.startswith(stem) and len(stem) >= 3:
            return "Modifier:Degree"
    for stem in MOD_QUANT_STEMS:
        if word.startswith(stem) and len(stem) >= 3:
            return "Modifier:Quantity"
    …

    return "Other"
```

## Multi‑Word Phrase Pre‑Tokenisation

Before splitting on whitespace / punctuation, replace known multi‑word
phrases with hyphenated tokens so they survive as single units:

```python
PHRASE_PATTERNS = {
    "small colonies":       "small-colonies",
    "very small colonies":  "very-small-colonies",
    "small colony":         "small-colony",
    "very small colony":    "very-small-colony",
}
DISPLAY_NAMES = {v: k for k, v in PHRASE_PATTERNS.items()}

def tokenise(text: str) -> list[str]:
    t = text.lower()
    for phrase, replacement in PHRASE_PATTERNS.items():
        t = t.replace(phrase, replacement)
    return [tok.strip(".,;:!?'")
            for tok in re.split(r"[,\s;:()]+", t)
            if tok.strip(".,;:!?'")]
```

The hyphenated tokens are classified by **exact match** before the
stem‑prefix fallback runs, so ``small-colonies`` is correctly picked up
as a Growth signal (not Morphology via the ``small`` stem).

When writing the output table, restore display names with
``pivot.rename(index=DISPLAY_NAMES)`` so the inspection spreadsheet
shows ``small colonies`` (no hyphen) while the classifier worked on
the internal hyphenated form.
```

## Pitfalls

1. **Short‑stem false positives.** A stem like `"a"` would match every
   word beginning with `"a"`. The `len(stem) >= 3` guard prevents this.

2. **Hyphenated compound tokens.** Multi-word phrases like
   ``small colonies`` should be internalised as a single hyphenated
   token (``small-colonies``) *before* tokenisation, so the exact‑match
   pass catches them. Algorithm: replace phrase → hyphenated form,
   then split on whitespace/punctuation.

3. **Priority order matters.** When a category set contains a word
   that is also a prefix of another category's word, check the more
   specific category first. The classifier should check Growth signal
   before Morphology, because ``small-colonies`` (growth) starts with
   ``small`` (morphology stem).

4. **Stem length trade-off.** Longer stems reduce false matches but
   may miss legitimate inflections. 4–6 characters is usually the
   sweet spot for biological text. Test with actual data.

5. **Data noise.** Fragmented tokens from dirty data (``wt/``,
   ``viable/essential``, ``32"``) cannot be handled by stem matching
   and will always fall through to ``Other``. This is acceptable —
   they are too rare to justify special handling.
