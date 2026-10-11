# Architecture

ResumeLens processes plain-text résumés through a transparent formal-language
pipeline. It checks whether a résumé's qualifications satisfy a profile pattern;
it does not score or rank candidates.

```text
Résumé text
   │
   ▼
Regex extraction ──► Surface forms
   │
   ▼
Finite-state transducers ──► Canonical qualifications
   │
   ▼
Profile sorter ──► One ordered sequence per profile
   │
   ▼
Finite automata ──► Verdict, trace, missing categories
   │
   ▼
Candidate DSL ──► textX validation ──► Markdown / HTML
```

## Module inputs and outputs

| Module | Responsibility | Input → output |
|---|---|---|
| `resumelens/profiles/` | Defines the four ordered category patterns and optional categories | Profile definitions → `Profile` objects |
| `resumelens/extraction/patterns.py` | Defines the formal languages recognized by each regex | Pattern specifications → compiled regular expressions |
| `resumelens/extraction/extractor.py` | Extracts candidate, contact, education, experience, and skill text | Résumé text → `ExtractionResult` |
| `resumelens/normalization/transducers.py` | Cleans surface forms and translates aliases through character-level FSTs | Raw skill strings → `Normalization` values and canonical skills |
| `resumelens/normalization/sorter.py` | Orders canonical skills against every profile's categories; retains unrelated skills | Canonical sequence → `SortedQualifications` per profile |
| `resumelens/recognition/automata.py` | Builds DFA/ε-NFA models, diagrams' edges, formal tuples, and a simulator | Profile categories and a word → automaton, tuple, acceptance result |
| `resumelens/recognition/classifier.py` | Reports each independent match with a state trace and missing categories | Profile sequences → `ProfileMatch` values |
| `resumelens/dsl/serializer.py` | Produces the textual candidate record | Candidate data → DSL source |
| `resumelens/dsl/validator.py` | Parses the grammar and checks semantic constraints | DSL source → `ValidationReport` |
| `resumelens/dsl/renderer.py` | Renders validated candidate data | textX model → Markdown and HTML |
| `resumelens/pipeline.py` | Connects all processing steps and keeps their intermediate outputs | Résumé text → `PipelineResult` |
| `ui/` and `app.py` | Collect résumé text and show extraction, normalization, recognition, DSL, and summary tabs | User input → interactive Streamlit results |

## Data flow and known limits

Every extracted skill is normalized, and unknown strings stay visible in the
normalization results but do not enter profile sequences. Each profile sequence
is independently sorted by category order, then classified without ranking.
The DSL is serialized and validated before its rendered previews are returned.

Experience years use the first integer in the first extracted years-of-
experience phrase. Education degrees and institutions are paired by their
appearance index because the regex extractor does not currently infer which
institution belongs to each degree. Résumé parsing is pattern-based and works
on plain text; it is not a semantic evaluator of job history.
