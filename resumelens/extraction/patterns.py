"""Regular expressions used to extract résumé information.

Each pattern documents the language (set of strings) it recognises. Patterns
only detect text that *may* be a qualification; deciding whether two spellings
are equivalent is the job of normalization.
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PatternSpec:
    name: str
    category: str
    regex: str
    language: str
    flags: int = re.IGNORECASE

    def compile(self) -> re.Pattern:
        return re.compile(self.regex, self.flags)


# A technology name must not be glued to other word characters: this avoids
# matching "JS" inside "JSON" or "Git" inside "GitHub".
_L = r"(?<![\w.])"
_R = r"(?![\w+#])"


def _term(*alternatives: str) -> str:
    return _L + "(?:" + "|".join(alternatives) + ")" + _R


# Capitalised word that stays case-sensitive under re.IGNORECASE.
_CAP = r"(?-i:[A-ZÁÉÍÓÚÑ])[\wáéíóúñ&]*"

CONTACT = "contact"
EXPERIENCE = "experience"
EDUCATION = "education"
LANGUAGES = "languages"
FRAMEWORKS = "frameworks"
DATABASES = "databases"
TOOLS = "tools"
OTHER = "other"

SKILL_CATEGORIES = (LANGUAGES, FRAMEWORKS, DATABASES, TOOLS, OTHER)

PATTERNS: tuple[PatternSpec, ...] = (
    # --- Contact information -------------------------------------------
    PatternSpec(
        "email", CONTACT,
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}",
        "A local part of letters, digits and . _ % + -, an '@', and a domain "
        "of dot-separated labels ending in a label of 2+ letters.",
        flags=0,
    ),
    PatternSpec(
        "phone", CONTACT,
        r"(?<![\w])(?:\+\d{1,3}[\s.-]?)?(?:\(\d{2,4}\)[\s.-]?)?\d{3}[\s.-]?\d{3,4}(?:[\s.-]?\d{2,4})?(?!\w)",
        "An optional '+country' prefix, an optional '(area)' and groups of "
        "digits separated by space, dot or hyphen; the extractor keeps only "
        "matches with 7 to 15 digits.",
        flags=0,
    ),
    PatternSpec(
        "url", CONTACT,
        r"(?:https?://|www\.)\S+|(?<![\w/.])(?:linkedin\.com/in|github\.com)/[\w./-]+",
        "A web address starting with http(s):// or www., or a LinkedIn / "
        "GitHub profile path without scheme, followed by non-space characters.",
    ),
    # --- Professional experience ---------------------------------------
    PatternSpec(
        "years_of_experience", EXPERIENCE,
        r"\b(\d{1,2})\+?\s*(?:years?|yrs?|años?)\s+(?:of\s+|de\s+)?(?:professional\s+)?(?:experience|experiencia)",
        "One or two digits, an optional '+', the word year(s)/yr(s)/año(s) and "
        "the word experience/experiencia, e.g. '3 years of experience'.",
    ),
    PatternSpec(
        "date_range", EXPERIENCE,
        r"\b(?:19|20)\d{2}\s*(?:-|–|—|to|a)\s*(?:(?:19|20)\d{2}|present|current|actualidad|presente)\b",
        "A year 19xx/20xx, a separator (- – — to a) and another year or the "
        "words present/current/presente/actualidad, e.g. '2019 - 2022'.",
    ),
    # --- Academic qualifications ---------------------------------------
    PatternSpec(
        "degree", EDUCATION,
        rf"\b(?:Ingenier[íi]a\s+(?:(?:de|en|del)\s+)?{_CAP}(?:\s+(?:(?:de|y)\s+)?{_CAP}){{0,2}}"
        rf"|(?:Bachelor(?:'s)?|Master(?:'s)?|Ph\.?D\.?|B\.?Sc\.?|M\.?Sc\.?|Associate(?:'s)?|Doctorate|Pregrado|Maestr[íi]a)(?![A-Za-z])"
        rf"(?:\s+(?:of|in|en|de)\s+{_CAP}(?:\s+{_CAP}){{0,3}}){{0,2}})",
        "Either 'Ingeniería' followed by an optional de/en/del and up to three "
        "capitalised words ('Ingeniería de Sistemas', 'Ingeniería Informática'), "
        "or a degree keyword (Bachelor, Master, PhD, B.Sc....) optionally "
        "followed by up to two 'of/in/en/de <Capitalised words>' groups, e.g. "
        "'Bachelor of Science in Computer Science'.",
    ),
    PatternSpec(
        "institution", EDUCATION,
        rf"\b(?:Universidad|University|Universit[ée]|Instituto|Institute|College)\s+(?:(?:of|de|del)\s+)?{_CAP}(?:\s+{_CAP}){{0,2}}",
        "An institution word (University, Universidad, Institute...) followed "
        "by an optional 'of/de/del' and up to three capitalised words.",
    ),
    # --- Programming languages -----------------------------------------
    PatternSpec(
        "language", LANGUAGES,
        _term(r"Java\s?Script", r"Type\s?Script", r"JS", r"TS", r"Python\s?3?", r"Java",
              r"C#", r"C\+\+", r"PHP", r"Ruby", r"Kotlin", r"Swift", r"Bash", r"Shell"),
        "A known programming-language name (JavaScript, JS, TypeScript, "
        "Python, Java, C#, C++, PHP, Ruby, Kotlin, Swift, Bash, Shell) not "
        "attached to other word characters.",
    ),
    # --- Frameworks and libraries --------------------------------------
    PatternSpec(
        "framework", FRAMEWORKS,
        _term(r"React(?:\.?\s?js)?", r"Angular(?:\.?\s?js)?", r"Vue(?:\.?\s?js)?",
              r"Node(?:\.\s?|\s)?js", r"Express(?:\.\s?|\s)?js", r"Next(?:\.\s?|\s)?js",
              r"Django", r"Flask", r"Fast\s?API", r"Spring[\s-]?Boot",
              r"Pandas", r"Num\s?Py", r"Scikit[-\s]?learn", r"sklearn",
              r"Tensor\s?Flow", r"Py\s?Torch", r"Keras", r"Py\s?Spark"),
        "A known framework or library name; the common variants are allowed "
        "(React / React.js / ReactJS, Node.js / NodeJS, Scikit-learn / "
        "scikit learn / sklearn, Tensor Flow / TensorFlow, Py Torch...).",
    ),
    # --- Databases -----------------------------------------------------
    PatternSpec(
        "database", DATABASES,
        _term(r"Postgre(?:\s?SQL|s)?", r"My\s?SQL", r"Maria\s?DB", r"SQL\s?Server",
              r"SQL\s?Lite", r"Mongo(?:\s?DB)?", r"Redis", r"Oracle(?:\s?DB)?",
              r"Cassandra", r"Dynamo\s?DB", r"Firebase", r"Big\s?Query",
              r"Snowflake", r"Redshift", r"SQL"),
        "A known database or query-language name (PostgreSQL / Postgres, "
        "MySQL, MongoDB / Mongo, SQL Server, BigQuery, SQL...).",
    ),
    # --- Tools and technologies ----------------------------------------
    PatternSpec(
        "tool", TOOLS,
        _term(r"(?:GitHub|GH)\s+Actions", r"GitLab[\s-]?CI(?:/CD)?", r"GitHub", r"GitLab",
              r"Bitbucket", r"Git", r"Docker", r"Kubernetes", r"K8s", r"Kube",
              r"Jenkins", r"Terraform", r"Ansible", r"Linux",
              r"AWS", r"Amazon\s+Web\s+Services", r"(?:Microsoft\s+)?Azure",
              r"GCP", r"Google\s+Cloud(?:\s+Platform)?", r"(?:Apache\s+)?Airflow",
              r"(?:Apache\s+)?Kafka", r"Jira", r"Postman"),
        "A known tool or platform name (Git, GitHub Actions, Docker, "
        "Kubernetes / K8s, AWS / Amazon Web Services, Airflow...).",
    ),
    # --- Other qualifications ------------------------------------------
    PatternSpec(
        "other", OTHER,
        _term(r"REST(?:ful)?\s+APIs?", r"Rest-APIs?", r"GraphQL", r"Machine[\s-]?Learning",
              r"Deep[\s-]?Learning", r"CI\s?/\s?CD", r"Agile", r"Scrum",
              r"Micro\s?services"),
        "Other qualifications relevant to the profiles: REST APIs, GraphQL, "
        "machine/deep learning, CI/CD, Agile, Scrum, microservices.",
    ),
)

NAME_PATTERN = PatternSpec(
    "name", CONTACT,
    rf"^[ \t]*({_CAP}(?:[ \t]+{_CAP}){{1,3}})[ \t]*$",
    "A line made only of two to four capitalised words (the candidate name); "
    "the extractor keeps the first such line.",
    flags=re.MULTILINE,
)


def as_markdown() -> str:
    """Documentation table of every pattern (used in docs/02-formalization.md)."""
    rows = ["| Name | Category | Regular expression | Recognised language |",
            "|---|---|---|---|"]
    for spec in (NAME_PATTERN, *PATTERNS):
        regex = spec.regex.replace("|", "\\|")
        rows.append(f"| {spec.name} | {spec.category} | `{regex}` | {spec.language} |")
    return "\n".join(rows)
