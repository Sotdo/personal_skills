# Signal-Based Classification Pattern

Replace brittle if-elif chains with a declarative signal table + resolution
engine. Every classification rule lives in data (a list of dataclass instances)
rather than in control flow.

## When to Use

You have a **rule-based classifier** that takes a text description and
produces a category label. The current implementation is a long `if-elif-else`
chain where:

- The ordering matters (the first match wins)
- Adding a new rule means finding the right insertion point
- Two rules can conflict and the earlier one silently wins
- The chain is 8+ branches long and growing

## The Pattern

### Step 1: Define a signal dataclass

```python
@dataclass(frozen=True, slots=True)
class Signal:
    keyword: str       # substring or regex to detect
    category: str      # label to assign
    tier: int          # priority / severity (optional)
```

### Step 2: Declare the signal table (a flat list)

```python
SIGNALS: list[Signal] = [
    Signal(keyword="very small colon", category="very small colonies", tier=4),
    Signal(keyword="small colon",      category="small colonies",      tier=4),
    Signal(keyword="microcolonies",    category="microcolonies",       tier=3),
    Signal(keyword="germinated",       category="germinated",          tier=2),
    Signal(keyword="divide",           category="germinated and divided", tier=2),
    Signal(keyword="spores",           category="spores",              tier=1),
]
```

Order more specific / longer patterns first so they match before shorter
substrings.

### Step 3: Detect all signals, then resolve

```python
def classify(description: str) -> tuple[str, int]:
    desc = description.lower()
    matched = [s for s in SIGNALS if s.keyword in desc]

    if not matched:
        return ("default", 5)          # fallback

    # Deduplicate categories
    categories = sorted({s.category for s in matched})
    # Remove redundant broader terms when a more specific one exists
    if "germinated and divided" in categories and "germinated" in categories:
        categories.remove("germinated")

    # ---- Signal-splitting check (before dedup) ----
    # Post-processing priority matters: if an earlier step removes a
    # category that a later step depends on, the later check silently
    # fails.  Here, a "spores implied by germinated" check must run
    # BEFORE "germinated implied by germinated-and-divided" — otherwise
    # "germinated" is already gone from the categories list and the
    # spores check vacuously passes.
    #
    # Use `any("germinated" in c for c in categories)` rather than
    # `"germinated" in categories` to catch both "germinated" and
    # "germinated and divided" after the former may have been removed.
    # -----------------------------------

    # ---- Contextual signal suppression ----
    # If a signal is only meaningful when it appears independently
    # (not as part of another signal's context), suppress it when
    # its "parent" signal is also present.
    #
    # Example: "germinated spores" — spores is part of the process
    #   of germination, not a separate dormant-spore population.
    #   But "spores, germinated spores" — the leading "spores"
    #   indicates a genuine mixed population.
    if "spores" in categories and any("germinated" in c for c in categories):
        _has_standalone = False
        for m in re.finditer(r"\bspores?\b", desc):
            before = desc[max(0, m.start() - 12) : m.start()].strip().rstrip(",")
            if before != "germinated":
                _has_standalone = True
                break
        if not _has_standalone:
            categories.remove("spores")
    # -----------------------------------

    # ---- Tier assignment: best outcome vs worst outcome ----
    # For a composite phenotype (multiple signals coexist), two choices:
    #
    #   tier = min(s.tier for s in matched)   # worst (most severe)
    #   tier = max(s.tier for s in matched)   # best (most advanced)
    #
    # "Best outcome" reflects the MOST ADVANCED growth stage the gene
    # can support — the informative endpoint.  "Worst outcome" is
    # conservative — reports the most severe defect.  Choice depends on
    # the research question.  This project uses **best outcome** because
    # the growth tier labels are used for GO enrichment / statistical
    # tests, and the most informative signal is the one that reveals
    # what the gene CAN do, not only what it can't.
    # -----------------------------------

    tier = max(s.tier for s in matched)

    return (", ".join(categories), tier)
```

## Why This Works

| Problem with if-elif | Solution with signal table |
|---|---|
| Ordering is fragile | All signals are detected independently — no ordering dependency |
| Adding a rule requires correct insertion | Add one line to `SIGNALS` — no structural change |
| Conflicts are implicit | All matches are collected; post-processing dedup is explicit |
| Categories are scattered across branches | Every category name appears exactly once in the signal table |
| Logic vs data are mixed | Table is pure data; the resolution function is pure logic |

## Pitfalls

1. **Substring collisions.** `"small colon"` matches `"very small colonies"`.
   Fix: order more specific patterns first and remove the broader match in
   post-processing.

2. **Composite category names can get long.** When 3+ signals coexist, the
   composed name can be unwieldy. Decide whether you need the full composite
   or if a summary tier is sufficient.

3. **Contextual signal suppression (a.k.a. the "germinated spores"
   problem).** A keyword can appear in the text in two very different
   contexts — as an independent concept (spores = dormant spores) or as
   part of a compound expression (germinated spores = an entity that has
   already germinated). A naive substring match treats both identically.
   Fix: use a lookbehind or context check in post-processing to suppress
   the signal when it's in the dependent context. The resolution is part of
   the classification function, not the signal table.

4. **The signal table is a global.** If the same classification is used
   across multiple scripts, extract the table to a shared module
   (e.g. `growth_signals.py`) so there is one source of truth.

5. **Performance.** `O(n * m)` in signal count × input size. For fewer than
   20 signals and <50K inputs it's negligible. For larger scales, compile
   the keywords into a single regex alternation.

---

## Extended Pattern: Comma‑Separated Description Analysis

When a description contains multiple comma‑separated segments, the
question is whether these represent *parallel phenotypes* (multi‑class)
or *secondary descriptions* (single class, extra detail).  The following
three‑rule engine decides, using the **last** comma‑separated segment as
the most significant split:

### The Rules

1. **Modifier‑first → secondary.** If the last segment starts with a
   frequency / degree word (``occasionally``, ``often``, ``some``,
   ``may``, ``sometimes``, etc.), it is a **secondary description**:
   the main phenotype is the first part. → **Single**

   *Example: ``germinated spores, often long and thin`` → Single*

2. **Contains a growth keyword → parallel.** If the last segment
   contains a canonical growth‑signal word (spores, germinated,
   microcolonies, small colon, etc.), it describes a **parallel growth
   phenotype**: the gene shows multiple distinct growth outcomes.
   → **Multiple**

   *Example: ``small colonies, germinated spores`` → Multiple*

3. **Otherwise → morphological supplement.** If the last segment is
   neither a modifier‑first clause nor a growth signal, it is a
   *morphology supplement* — shape/state detail that does not change the
   growth classification. → **Single**

   *Example: ``small colonies, slightly misshapen`` → Single*

### Reference Implementation

```python
MODIFIER_WORDS = (
    # Frequency
    "occasionally", "often", "occasional", "sometimes",
    "mostly", "rarely", "frequently", "frequency", "rare",
    "possible", "may", "possibly", "rapidly", "initially",
    # Degree
    "slightly", "very", "highly", "barely", "slight", "high", "weak",
    # Quantity
    "some", "many", "few", "lots", "several", "multiple",
    "once", "twice", "more", "multi",
)
GROWTH_KEYWORDS = (
    "spores", "germinated", "germination", "microcolonies",
    "small colon", "very small colon", "divide", "division",
)
```

**Critical downstream follow-up.** When the comma suffix has been
classified as secondary / supplementary (the function returned
``"Single"``), any downstream *growth classification* script MUST pass
**only the text before the first comma** to the classification engine.
If the suffix contains a growth word (e.g. ``"some germination long"``),
the downstream classifier would otherwise detect it and produce an
incorrect category.  Rule:

- ``Phenotype_count == "Single"`` → pass ``text.split(",", 1)[0].strip()``
- ``Phenotype_count == "Multiple"`` → pass the full description

### Why Last Segment Only

In bioinformatics phenotype descriptions, the most informative split is
the **last comma**: earlier commas often list coordinate morphology
terms (``long, branched, septated``) that belong to the same phenotype,
while the final segment determines whether a truly separate growth
outcome is described.
