# Architecture

Pipeline: regex extraction -> normalization (transducers) -> classification (automata) -> DSL (textX) -> HTML/Markdown.

Only completed requirements are listed.

| Module | Role | Input -> Output | Status |
|---|---|---|---|
| `resumelens/profiles/` | Declarative profiles: ordered categories of canonical qualifications | - -> `Profile` | done |
| `resumelens/normalization/aliases.py` | Alias table, `alias_key`, `canonical_of` | surface form -> canonical name | done |
| `resumelens/extraction/` | Regex extraction of résumé information | résumé text -> `ExtractionResult` | done |
