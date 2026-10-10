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
