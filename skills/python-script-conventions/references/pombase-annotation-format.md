# PomBase Gene Annotation: gene_IDs_names_products.tsv

## Source

```
https://www.pombase.org/monthly_releases/{year}/pombase-{release}/gene_names_and_identifiers/gene_IDs_names_products.tsv
```

- `{year}` — 4-digit year (e.g. `2026`)
- `{release}` — full release tag (e.g. `2026-06-01`)
- Monthly releases listed at: <https://www.pombase.org/monthly_releases/{year}/>

## Columns (8)

| # | Column | Type | Example | Notes |
|---|--------|------|---------|-------|
| 1 | `gene_systematic_id` | str | `SPAC1002.01` | PomBase stable systematic ID |
| 2 | `gene_systematic_id_with_prefix` | str | `PomBase:SPAC1002.01` | Same ID with DB prefix |
| 3 | `gene_name` | str | `mrx11` | Current standard gene symbol (empty if none) |
| 4 | `chromosome_id` | str | `chromosome_1` | Chromosome assignment |
| 5 | `gene_product` | str | `mitochondrial matrix protein` | Product description |
| 6 | `external_id` | str | `Q9UR06` | UniProt accession (protein-coding only) |
| 7 | `gene_type` | str | `protein coding gene` | Feature type ontology term |
| 8 | `synonyms` | str | `SPAC1610.05` | Comma-separated old names/aliases |

## Key gene_type values

- `protein coding gene` — main category (filter for protein-coding)
- `pseudogene` — non-functional remnants
- `tRNA gene`, `rRNA gene`, `snoRNA gene`, `snRNA gene`, `lncRNA gene`, `sncRNA gene` — RNA genes

## Usage in systematic ID update

The `update_sysIDs()` function uses this file to map Hayles 2013 table IDs through three layers:

1. **Direct systematic ID** — check if the ID still exists in `gene_systematic_id`
2. **Gene name lookup** — check if the old `Gene name` matches `gene_name` of a different systematic ID
3. **Synonym lookup** — check if the old systematic ID appears in the `synonyms` column (comma-separated)

### Synonyms format

```
SPAC1610.05, old_name2, SPAC1234.01
```

Comma-separated, no spaces between entries. Some entries are old systematic IDs, others are historical gene names.

## Total records

~12,685 rows (protein coding + RNA + pseudogenes), ~1.3 MB gzipped.

Last updated: 2026-06-01 for the 2026-06 monthly release.
