# Test cases

Run all tests with `pytest -q`. Each test file covers one module, and the
`samples/*.txt` résumés are shared fixtures.

**Convention:** whoever adds a module also adds its section here, in the same
commit as its tests. Each section lists what is tested, the input, the expected
result and the reason.

## Sample résumés (`samples/`)

| File | Content | Used to check |
|---|---|---|
| `wednesday_addams.txt` | JS, React.js, NodeJS, Postgres, Git (example of the task statement) | Full Stack extraction |
| `mary_jane_watson.txt` | Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git (example of the task statement) | Machine Learning Engineer extraction |
| `full_stack_complete.txt` | Contact data, degree, institution, date ranges, REST APIs, GitHub, Docker... | Contact, education and experience patterns; GitHub as version control |
| `devops_engineer.txt` | Python, Bash, Docker, k8s, Jenkins, Amazon Web Services, Terraform, Git | DevOps alias variants |
| `data_engineer.txt` | Python, SQL, Py Spark, Apache Airflow, BigQuery, Git | Data Engineer alias variants |
| `noisy_spelling_variants.txt` | Javascript, ReactJS, Node js, sklearn, scikit learn, Tensor Flow, Py Torch... plus "JSON" | Many spellings of one qualification; no false match inside "JSON" |
| `rejected_missing_version_control.txt` | JavaScript, React, Postgres, no Git | A résumé that must not satisfy a profile |

## Résumé information extraction (`tests/test_extraction.py`)

| Test | Input | Expected | Why |
|---|---|---|---|
| `test_wednesday_addams_matches_statement` | `wednesday_addams.txt` | name "Wednesday Addams"; skills `JS, React.js, NodeJS, Postgres, Git`; "3 years of experience" | Reproduces the extraction example of the task statement |
| `test_mary_jane_watson` | `mary_jane_watson.txt` | skills in order of appearance, 7 items | Second reference résumé |
| `test_contact_information` | `full_stack_complete.txt` | one email, phone `+57 300 123 4567`, GitHub and LinkedIn URLs | Contact patterns |
| `test_urls_and_emails_are_not_technologies` | same | "GitHub" appears once; the URL `github.com` is not read as a tool | Overlapping matches must not duplicate a qualification |
| `test_education_and_experience` | same | degree, institution, two date ranges, "4+ years of experience", REST APIs in `other` | Education and experience patterns |
| `test_word_boundaries` | `JSON, GitHub, NoSQL, javascripting` | only `GitHub` | "JS" is not found inside "JSON"; "SQL" is not found inside "NoSQL" |
| `test_nodejs_is_not_also_js` | `Node.js` | `["Node.js"]` | Longest match wins over the `js` suffix |
| `test_short_digit_runs_are_not_phones` | `Worked 2019 - 2022 on 12345 things` | no phone | Phones need 7 to 15 digits |
| `test_empty_text` | empty string | no name, no skills | Edge case |
| `test_every_extracted_skill_has_a_canonical_form` (7 files) | each sample | every extracted string has a canonical form in the alias table | What extraction detects can always be normalized later |
| `test_save_json` | `wednesday_addams.txt` | JSON file contains "React.js" | The result can be saved to a file, as the task requires |
| `test_degrees` (5 cases) | "Ingeniería de Sistemas", "Ingeniería Informática", "Ingeniería de Sistemas y Computación", "Bachelor of Science in Computer Science", "B.Sc. in Mathematics" | the full degree text | Degree pattern, in Spanish and English |
| `test_ingenieria_alone_is_not_a_degree` | `trabajo de ingeniería general` | no degree | The pattern needs capitalised words after "Ingeniería" |

## Alias table (`tests/test_aliases.py`)

| Test | Input | Expected | Why |
|---|---|---|---|
| `test_equivalent_spellings` (17 cases) | `JS`, `Javascript`, `React.js`, `ReactJS`, `NodeJS`, `Node.js`, `Postgres`, `PostgreSQL`, `sklearn`, `scikit learn`, `Scikit-learn`, `Tensor Flow`, `TensorFlow`, `Py Torch`, `pandas`, `k8s`, `Amazon Web Services` | `JAVASCRIPT`, `REACT`, `NODE_JS`, `POSTGRESQL`, `SCIKIT_LEARN`, `TENSORFLOW`, `PYTORCH`, `PANDAS`, `KUBERNETES`, `AWS` | Equivalent spellings map to one canonical name |
| `test_unknown_is_none` | `COBOL-ish thing` | `None` | Unknown text is not invented as a qualification |

An ambiguous alias (the same spelling for two qualifications) makes the module fail
when it is imported, so it cannot reach the tests.

## Professional profiles (`tests/test_profiles.py`)

| Test | Checks | Why |
|---|---|---|
| `test_four_profiles_are_defined` | `full_stack`, `ml_engineer`, `devops_engineer`, `data_engineer` exist | The task requires four profiles in the same solution |
| `test_every_profile_skill_has_aliases` | every qualification of every profile has an alias entry | Normalization can produce every qualification a profile expects |
| `test_canonical_order_follows_categories` | in Full Stack: JAVASCRIPT < REACT < NODE_JS < POSTGRESQL < GIT; PYTHON is not part of it | Canonical order of the task statement |
| `test_no_empty_categories` | every category has at least one qualification | A category without options could never be satisfied |
| `test_version_control_hosts_count_as_git` | GIT, GITHUB, GITLAB and BITBUCKET are in "Version control" in all profiles | Design decision: a code host implies Git |
| `test_declared_automaton_types` | ML and Data are DFA; Full Stack and DevOps are ε-NFA | Types to be justified with the definition |
| `test_categories_of_a_profile_do_not_share_skills` | no qualification appears twice in a profile | Keeps the automaton deterministic where it must be |
| `test_epsilon_nfa_profiles_have_an_optional_category` | a profile has an optional category only if it is an ε-NFA | An ε-transition is needed only to skip an optional category |

## Diagram builder (`tests/test_diagrams.py`)

| Test | Checks | Why |
|---|---|---|
| `test_final_states_are_double_circles` | final states use `doublecircle`, others `circle` | Standard notation for accepting states |
| `test_start_arrow_points_to_start_state` | an arrow goes into the start state | Standard notation for the initial state |
| `test_parallel_edges_are_merged` | `PANDAS` and `NUMPY` between the same states give one edge labelled "PANDAS, NUMPY" | Same style as the task statement figures |
| `test_parallel_edges_can_stay_separate` | with `merge_parallel=False` there are two edges | Needed to draw transducers with different outputs |
| `test_duplicate_labels_are_not_repeated` | the same label twice is drawn once | Avoids "X, X" |
| `test_export_svg` | an SVG file is written | Requires the Graphviz program; skipped if it is not installed |

## Qualification normalization transducers (`tests/test_transducers.py`)

| Test | Input / Checks | Expected | Why |
|---|---|---|---|
| `test_pyformlang_fst_smoke` | Minimal 2-state FST with transitions on "a" | `[["X"]]` on "a", `[]` on "b" | Verifies pyformlang FST translation generator semantics |
| `test_clean_fst_equivalent_to_alias_key` | All 228 surface forms in `ALIASES` | `clean(form) == alias_key(form)` | Ensures T_clean matches the canonical cleaning key |
| `test_clean_fst_separators_and_case` | "Node.js", "React.js", "C++", "C#", "Spring-Boot", "CI/CD", "Amazon Web Services", "Postgre SQL" | "nodejs", "reactjs", "c++", "c#", "springboot", "cicd", "amazonwebservices", "postgresql" | Lower-casing and deletion of `.`, `-`, `_`, `/` and spaces |
| `test_clean_fst_empty` | Empty string `""` | `""` | Empty string edge case on start/final state q0 |
| `test_clean_fst_invalid_char` | `"@invalid!"` | `None` | Characters outside the cleaning alphabet reject the path |
| `test_every_alias_form_translates_to_canonical` | All 228 surface forms in `ALIASES` | `translate(form) == canonical_of(form) == canonical` | Two-level transducer maps every known alias to its canonical qualification |
| `test_end_marker_resolves_prefixes` | "Java" vs "JavaScript", "Git" vs "GitHub" | "JAVA", "JAVASCRIPT", "GIT", "GITHUB" | The `$` end marker distinguishes prefix overlaps in the trie |
| `test_unknown_and_json_are_none` | "JSON", "COBOL-ish thing", "unknown_tool", `""` | `None` | Unknown qualifications and false substrings are not recognized |
| `test_fst_tuples_are_consistent` | All 6 transducers (`clean` and the 5 group lexicons) | `is_consistent() == True` | Start/final states are in Q, transitions stay strictly within Q, Σ, Γ |
| `test_fst_tuple_edges_format` | Edges from T_clean and T_lex_tools | Transitions with format `a : a`, `. : ε`, `$ : GIT` | Formats transitions for graphviz visualization |
| `test_fst_tuple_as_markdown` | T_clean tuple | Markdown headers, state counts, transition table | Formal documentation rendering |
| `test_normalize_all` | `["React.js", "Python", "JSON", "Docker"]` | 4 `Normalization` objects with raw and canonical values | Preserves extraction items with their canonical mapping |
| `test_canonical_skills_dedupes_and_filters_none` | `["React.js", "Python", "JSON", "React", "Docker", "Python 3"]` | `("REACT", "PYTHON", "DOCKER")` | Drops None and duplicates while preserving first appearance |
| `test_canonical_skills_empty` | `[]` | `()` | Empty collection edge case |
| `test_custom_lexicon_build` | Custom lexicon with "TOOL_A" and "TOOL_B" | Translates "toola$" to "TOOL_A", rejects without `$` | Generative trie builder works on arbitrary alias sets |
| `test_transducers_dict_keys` | Transducers dictionary | Contains `clean`, `languages`, `frameworks`, `databases`, `tools`, `other` | All five skill categories plus cleaning are available |

## Profile-driven canonical sorting (`tests/test_sorter.py`)

| Test | Input / Checks | Expected | Why |
|---|---|---|---|
| `test_task_statement_full_stack_order` | `GIT, NODE_JS, JAVASCRIPT, POSTGRESQL, REACT` | `JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT` | Reproduces the exact canonical sorting example from the task statement |
| `test_ignored_skills_routed_separately` | `PYTHON, DOCKER, JAVASCRIPT, GIT, AWS` for Full Stack | sequence: `JAVASCRIPT, GIT`; ignored: `PYTHON, DOCKER, AWS` | Skills outside the profile are not discarded silently but reported in `ignored` |
| `test_deduplication` | `JAVASCRIPT, REACT, JAVASCRIPT, REACT, GIT` | sequence: `JAVASCRIPT, REACT, GIT`; ignored: `()` | Repeated qualifications are pruned to their first appearance |
| `test_multiple_skills_in_same_category_preserves_original_order` | `NUMPY, PYTHON, PANDAS, GIT` for ML Engineer | sequence: `PYTHON, NUMPY, PANDAS, GIT` | Multiple skills within the same category preserve their relative order of appearance |
| `test_empty_canonicals` | `[]` for Full Stack | sequence: `()`; ignored: `()` | Empty qualifications edge case |
| `test_all_ignored` | `AWS, DOCKER, KUBERNETES` for Full Stack | sequence: `()`; ignored: `AWS, DOCKER, KUBERNETES` | Entirely non-matching input routed to `ignored` |
| `test_sort_for_all` | `PYTHON, SQL, PANDAS, GIT, REACT` across all 4 profiles | Result contains all 4 profile keys; profile-specific sequences and ignored lists | Evaluates sorting for all profiles in one call |
| `test_devops_profile_sorting` | `GIT, TERRAFORM, AWS, JENKINS, DOCKER, PYTHON, KUBERNETES` | `PYTHON, DOCKER, KUBERNETES, JENKINS, AWS, TERRAFORM, GIT` | Validates canonical category ordering for DevOps Engineer |
| `test_data_engineer_profile_sorting` | `GIT, BIGQUERY, AIRFLOW, PANDAS, SQL, PYTHON` | `PYTHON, SQL, PANDAS, AIRFLOW, BIGQUERY, GIT` | Validates canonical category ordering for Data Engineer |

## Candidate DSL (`tests/test_dsl.py`)

| Test | Input / Checks | Expected | Why |
|---|---|---|---|
| `test_serializer_round_trip_is_valid` | Candidate data with contact, experience, education, skills and two profile results | `validate(to_dsl(data)).valid` is true and string delimiters are escaped | Confirms the serializer emits grammar accepted by textX |
| `test_empty_name_becomes_unknown` | Candidate whose name is empty | The DSL stores `"Unknown"` and validates | Documents the required fallback identity |
| `test_invalid_sources_are_rejected` (8 cases) | Missing closing brace, lower-case skill, unknown profile, accepted profile without sequence, unclosed string, repeated category, unknown canonical, and a sequence outside a profile alphabet | Every source is invalid with a syntax/lexical or semantic error | Covers the language rejection rules and profile-alphabet constraints |
| `test_markdown_renderer_includes_candidate_and_verdict` | Parsed candidate with accepted and rejected profile results | Markdown includes candidate name and both verdicts | Confirms the summary contains the recognition outcome |
| `test_html_renderer_escapes_text_and_shows_verdict_badges` | Candidate name containing markup and accepted/rejected results | Markup is escaped and both badge classes appear | Prevents model text from becoming executable HTML and distinguishes outcomes |

## Profile automata (`tests/test_automata.py`)

| Test | Input / Checks | Expected | Why |
|---|---|---|---|
| `test_each_profile_automaton_kind_matches_its_definition` | Each generated transition table | ML and Data are DFA; Full Stack and DevOps are ε-NFA | Confirms implementation matches the declared formal model |
| `test_profile_automata_accept_and_reject_expected_sequences` | One complete sequence and its missing-version-control prefix for each profile | Complete sequences accepted; incomplete sequences rejected by pyformlang and the independent simulator | Verifies category ordering and final-state behavior |
| `test_full_stack_accepts_with_and_without_optional_api` | Full Stack sequence with and without REST_API | Both accepted | The optional category is skipped through ε |
| `test_full_stack_rejects_missing_version_control` | Full Stack sequence without GIT/GITHUB/GITLAB/BITBUCKET | Rejected | Version control is mandatory |
| `test_choices_within_category_are_alternatives` | ML profile using PANDAS or NUMPY | Both sequences accepted | Each category offers alternatives, not an all-of requirement |
| `test_tuple_exposes_states_alphabet_and_regex` | Generated Full Stack five-tuple | q0 start, q6 final, optional REST_API marked with `*` | Exposes a formal model suitable for docs and diagrams |
| `test_infer_kind_detects_nondeterminism_and_epsilon` | Competing destinations and an epsilon edge | NFA and ε-NFA respectively | Checks the formal type inference rules |

## Profile classifier (`tests/test_classifier.py`)

| Test | Input / Checks | Expected | Why |
|---|---|---|---|
| `test_classify_accepts_full_stack_and_reports_trace` | Complete Full Stack canonical sequence | Accepted with a state trace and no missing categories | Makes the recognition decision explainable |
| `test_classify_rejects_and_reports_missing_category` | Full Stack sequence without version control | Rejected; Version control is reported missing | Exposes why a profile did not match |
| `test_classify_all_preserves_profile_order_without_ranking` | Different sequences for all four profiles | One result per profile in declaration order | Classification checks each profile independently |
| `test_accepted_profiles_returns_all_matches` | Several accepted profile results | Every accepted result returned in profile order | A résumé can satisfy multiple profiles; there is no score or ranking |
| `test_unknown_profile_raises_key_error` | Unknown profile key | `KeyError` | Prevents silent classifications against undefined profiles |

## Full Streamlit pipeline (`tests/test_pipeline.py`)

| Test | Input | Expected | Why |
|---|---|---|---|
| `test_pipeline_produces_valid_dsl_and_all_profile_results` | Wednesday Addams sample | Valid `PipelineResult`, all four profile sequences, valid DSL, Markdown and HTML | Confirms each pipeline output is available to the application views |
| `test_pipeline_classifies_reference_full_stack_resume` | Wednesday Addams sample | `full_stack` is the only accepted profile | Confirms the app's integrated result matches the task example |

## End-to-end pipeline (`tests/test_pipeline.py`)

| Test | Input | Expected output | Why |
|---|---|---|---|
| `test_end_to_end_reference_samples_match_expected_profiles` | All seven `samples/*.txt` CVs | Wednesday and complete Full Stack → Full Stack; Mary Jane → ML; DevOps → DevOps; Bruce Banner → Data; rejected and noisy CVs → no accepted profile; every DSL validates | Checks every documented example from raw text through classification |
| `test_missing_version_control_is_explained_in_end_to_end_result` | `rejected_missing_version_control.txt` | No acceptance; Full Stack reports Version control missing | Confirms useful rejection feedback at the end of the pipeline |
| `test_noisy_variants_normalize_without_duplicates_and_do_not_match` | `noisy_spelling_variants.txt` | Repeated spellings collapse to canonical skills; no profile accepted | Confirms alias handling while preventing an incomplete résumé from matching |
