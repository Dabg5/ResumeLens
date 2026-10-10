# Formalization

## Résumé information extraction: regular expressions (`resumelens/extraction/patterns.py`)

Each pattern is implemented with Python's `re` module. Extraction only *detects*
text that may be a qualification; it does not decide equivalence between
spellings (normalization) or whether the candidate satisfies a profile (pattern recognition).
Technology patterns use `(?<![\w.])` / `(?![\w+#])` guards so `JS` is not found
inside `JSON` or `Node.js`, and `Git` is not found inside `GitHub`. When several
technology matches overlap, the earliest and longest wins; emails and URLs are
never read as technologies.

| Name | Category | Regular expression | Recognised language |
|---|---|---|---|
| name | contact | `^[ \t]*((?-i:[A-ZÁÉÍÓÚÑ])[\wáéíóúñ&]*(?:[ \t]+(?-i:[A-ZÁÉÍÓÚÑ])[\wáéíóúñ&]*){1,3})[ \t]*$` | A line made only of two to four capitalised words (the candidate name); the extractor keeps the first such line. |
| email | contact | `[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}` | A local part of letters, digits and . _ % + -, an '@', and a domain of dot-separated labels ending in a label of 2+ letters. |
| phone | contact | `(?<![\w])(?:\+\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)[\s.-]?)?\d{3}[\s.-]?\d{3,4}(?:[\s.-]?\d{2,4})?(?!\w)` | An optional '+country' prefix, an optional '(area)' and groups of digits separated by space, dot or hyphen; the extractor keeps only matches with 7 to 15 digits. |
| url | contact | `(?:https?://\|www\.)\S+\|(?<![\w/.])(?:linkedin\.com/in\|github\.com)/[\w./-]+` | A web address starting with http(s):// or www., or a LinkedIn / GitHub profile path without scheme, followed by non-space characters. |
| years_of_experience | experience | `\b(\d{1,2})\+?\s*(?:years?\|yrs?\|años?)\s+(?:of\s+\|de\s+)?(?:professional\s+)?(?:experience\|experiencia)` | One or two digits, an optional '+', the word year(s)/yr(s)/año(s) and the word experience/experiencia, e.g. '3 years of experience'. |
| date_range | experience | `\b(?:19\|20)\d{2}\s*(?:-\|–\|—\|to\|a)\s*(?:(?:19\|20)\d{2}\|present\|current\|actualidad\|presente)\b` | A year 19xx/20xx, a separator (- – — to a) and another year or the words present/current/presente/actualidad, e.g. '2019 - 2022'. |
| degree | education | `\b(?:Bachelor(?:'s)?\|Master(?:'s)?\|Ph\.?D\.?\|B\.?Sc\.?\|M\.?Sc\.?\|Associate(?:'s)?\|Doctorate\|Pregrado\|Maestr[íi]a\|Ingenier[íi]a)(?![A-Za-z])(?:\s+(?:of\|in\|en\|de)\s+(?-i:[A-ZÁÉÍÓÚÑ])[\wáéíóúñ&]*(?:\s+(?-i:[A-ZÁÉÍÓÚÑ])[\wáéíóúñ&]*){0,3}){0,2}` | A degree keyword (Bachelor, Master, PhD, B.Sc., Ingeniería...) optionally followed by up to two 'of/in/en/de <Capitalised words>' groups, e.g. 'Bachelor of Science in Computer Science'. |
| institution | education | `\b(?:Universidad\|University\|Universit[ée]\|Instituto\|Institute\|College)\s+(?:(?:of\|de\|del)\s+)?(?-i:[A-ZÁÉÍÓÚÑ])[\wáéíóúñ&]*(?:\s+(?-i:[A-ZÁÉÍÓÚÑ])[\wáéíóúñ&]*){0,2}` | An institution word (University, Universidad, Institute...) followed by an optional 'of/de/del' and up to three capitalised words. |
| language | languages | `(?<![\w.])(?:Java\s?Script\|Type\s?Script\|JS\|TS\|Python\s?3?\|Java\|C#\|C\+\+\|PHP\|Ruby\|Kotlin\|Swift\|Bash\|Shell)(?![\w+#])` | A known programming-language name (JavaScript, JS, TypeScript, Python, Java, C#, C++, PHP, Ruby, Kotlin, Swift, Bash, Shell) not attached to other word characters. |
| framework | frameworks | `(?<![\w.])(?:React(?:\.?\s?js)?\|Angular(?:\.?\s?js)?\|Vue(?:\.?\s?js)?\|Node(?:\.\s?\|\s)?js\|Express(?:\.\s?\|\s)?js\|Next(?:\.\s?\|\s)?js\|Django\|Flask\|Fast\s?API\|Spring[\s-]?Boot\|Pandas\|Num\s?Py\|Scikit[-\s]?learn\|sklearn\|Tensor\s?Flow\|Py\s?Torch\|Keras\|Py\s?Spark)(?![\w+#])` | A known framework or library name; the common variants are allowed (React / React.js / ReactJS, Node.js / NodeJS, Scikit-learn / scikit learn / sklearn, Tensor Flow / TensorFlow, Py Torch...). |
| database | databases | `(?<![\w.])(?:Postgre(?:\s?SQL\|s)?\|My\s?SQL\|Maria\s?DB\|SQL\s?Server\|SQL\s?Lite\|Mongo(?:\s?DB)?\|Redis\|Oracle(?:\s?DB)?\|Cassandra\|Dynamo\s?DB\|Firebase\|Big\s?Query\|Snowflake\|Redshift\|SQL)(?![\w+#])` | A known database or query-language name (PostgreSQL / Postgres, MySQL, MongoDB / Mongo, SQL Server, BigQuery, SQL...). |
| tool | tools | `(?<![\w.])(?:(?:GitHub\|GH)\s+Actions\|GitLab[\s-]?CI(?:/CD)?\|GitHub\|GitLab\|Bitbucket\|Git\|Docker\|Kubernetes\|K8s\|Kube\|Jenkins\|Terraform\|Ansible\|Linux\|AWS\|Amazon\s+Web\s+Services\|(?:Microsoft\s+)?Azure\|GCP\|Google\s+Cloud(?:\s+Platform)?\|(?:Apache\s+)?Airflow\|(?:Apache\s+)?Kafka\|Jira\|Postman)(?![\w+#])` | A known tool or platform name (Git, GitHub Actions, Docker, Kubernetes / K8s, AWS / Amazon Web Services, Airflow...). |
| other | other | `(?<![\w.])(?:REST(?:ful)?\s+APIs?\|Rest-APIs?\|GraphQL\|Machine[\s-]?Learning\|Deep[\s-]?Learning\|CI\s?/\s?CD\|Agile\|Scrum\|Micro\s?services)(?![\w+#])` | Other qualifications relevant to the profiles: REST APIs, GraphQL, machine/deep learning, CI/CD, Agile, Scrum, microservices. |

Result structure: `ExtractionResult` (`resumelens/extraction/extractor.py`),
serialisable to JSON with `ExtractionResult.save()`. Its `skills` list keeps every
technology string in order of appearance and is the input of the normalization step.
