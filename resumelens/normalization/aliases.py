"""Alias table: canonical qualification -> equivalent surface forms.

This is the single source of truth for stage 2. The transducers are built
from it, so every spelling listed here becomes a path in a transducer.
"""
import re

ALIASES: dict[str, tuple[str, ...]] = {
    # Languages
    "JAVASCRIPT": ("JS", "JavaScript", "Javascript", "Java Script", "ECMAScript"),
    "TYPESCRIPT": ("TS", "TypeScript", "Typescript", "Type Script"),
    "PYTHON": ("Python", "Python3", "Python 3"),
    "JAVA": ("Java",),
    "CSHARP": ("C#", "CSharp", "C Sharp"),
    "CPP": ("C++", "CPP"),
    "PHP": ("PHP",),
    "RUBY": ("Ruby",),
    "KOTLIN": ("Kotlin",),
    "SWIFT": ("Swift",),
    "BASH": ("Bash", "Shell", "Shell scripting"),
    # Frameworks and libraries
    "REACT": ("React", "React.js", "ReactJS", "React JS"),
    "ANGULAR": ("Angular", "Angular.js", "AngularJS", "Angular JS"),
    "VUE": ("Vue", "Vue.js", "VueJS", "Vue JS"),
    "NODE_JS": ("Node.js", "NodeJS", "Node JS", "Node js"),
    "EXPRESS": ("Express.js", "ExpressJS", "Express JS"),
    "NEXT_JS": ("Next.js", "NextJS", "Next JS"),
    "DJANGO": ("Django",),
    "FLASK": ("Flask",),
    "FASTAPI": ("FastAPI", "Fast API"),
    "SPRING_BOOT": ("Spring Boot", "SpringBoot", "Spring-Boot"),
    "PANDAS": ("pandas", "Pandas"),
    "NUMPY": ("NumPy", "Numpy", "Num Py"),
    "SCIKIT_LEARN": ("sklearn", "scikit learn", "Scikit-learn", "Scikit learn", "scikitlearn"),
    "TENSORFLOW": ("TensorFlow", "Tensor Flow", "Tensorflow"),
    "PYTORCH": ("PyTorch", "Py Torch", "Pytorch"),
    "KERAS": ("Keras",),
    "PYSPARK": ("PySpark", "Py Spark", "pyspark"),
    # Databases and query languages
    "SQL": ("SQL", "Sql"),
    "POSTGRESQL": ("Postgres", "PostgreSQL", "Postgre", "Postgre SQL", "PostgreSql"),
    "MYSQL": ("MySQL", "My SQL"),
    "MARIADB": ("MariaDB", "Maria DB"),
    "SQLITE": ("SQLite", "SQL Lite"),
    "SQL_SERVER": ("SQL Server", "SQLServer", "MS SQL", "MSSQL"),
    "ORACLE": ("Oracle", "Oracle DB"),
    "MONGODB": ("Mongo", "MongoDB", "Mongo DB"),
    "REDIS": ("Redis",),
    "CASSANDRA": ("Cassandra",),
    "DYNAMODB": ("DynamoDB", "Dynamo DB"),
    "FIREBASE": ("Firebase",),
    "BIGQUERY": ("BigQuery", "Big Query"),
    "SNOWFLAKE": ("Snowflake",),
    "REDSHIFT": ("Redshift", "Red Shift"),
    # Tools and technologies
    "GIT": ("Git",),
    "GITHUB": ("GitHub", "Github"),
    "GITLAB": ("GitLab", "Gitlab"),
    "BITBUCKET": ("Bitbucket", "Bit Bucket"),
    "DOCKER": ("Docker",),
    "KUBERNETES": ("Kubernetes", "K8s", "Kube"),
    "JENKINS": ("Jenkins",),
    "GITHUB_ACTIONS": ("GitHub Actions", "GH Actions", "Github Actions"),
    "GITLAB_CI": ("GitLab CI", "GitLab CI/CD", "Gitlab-CI"),
    "TERRAFORM": ("Terraform",),
    "ANSIBLE": ("Ansible",),
    "LINUX": ("Linux",),
    "AWS": ("AWS", "Amazon Web Services"),
    "AZURE": ("Azure", "Microsoft Azure"),
    "GCP": ("GCP", "Google Cloud", "Google Cloud Platform"),
    "AIRFLOW": ("Airflow", "Apache Airflow"),
    "KAFKA": ("Kafka", "Apache Kafka"),
    "JIRA": ("Jira",),
    "POSTMAN": ("Postman",),
    # Other qualifications
    "REST_API": ("REST API", "REST APIs", "RESTful API", "RESTful APIs", "Rest-API"),
    "GRAPHQL": ("GraphQL", "Graph QL"),
    "MACHINE_LEARNING": ("Machine Learning", "Machine-Learning"),
    "DEEP_LEARNING": ("Deep Learning", "Deep-Learning"),
    "CI_CD": ("CI/CD", "CICD", "CI CD"),
    "AGILE": ("Agile",),
    "SCRUM": ("Scrum",),
    "MICROSERVICES": ("Microservices", "Micro services"),
}


def alias_key(text: str) -> str:
    """Comparison key: lower case and no separators.

    'Node.js', 'node js' and 'NodeJS' all become 'nodejs'.
    """
    return re.sub(r"[^a-z0-9+#]", "", text.lower())


def _build_lookup() -> dict[str, str]:
    lookup: dict[str, str] = {}
    for canonical, forms in ALIASES.items():
        for form in (canonical, *forms):
            key = alias_key(form)
            if lookup.setdefault(key, canonical) != canonical:
                raise ValueError(
                    f"alias {form!r} is ambiguous: {lookup[key]} vs {canonical}"
                )
    return lookup


ALIAS_LOOKUP: dict[str, str] = _build_lookup()


def canonical_of(text: str) -> str | None:
    """Canonical qualification for a surface form, or None if unknown."""
    return ALIAS_LOOKUP.get(alias_key(text))
