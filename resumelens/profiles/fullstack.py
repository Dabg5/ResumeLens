from .base import Category, Profile

FULL_STACK = Profile(
    key="full_stack",
    name="Full Stack Developer",
    description=(
        "Client-side and server-side development: a frontend language and "
        "framework, a backend technology, a SQL/NoSQL database and Git. "
        "REST APIs are optional."
    ),
    automaton_type="ε-NFA",
    categories=(
        Category("Frontend language", ("JAVASCRIPT", "TYPESCRIPT")),
        Category("Frontend framework", ("REACT", "ANGULAR", "VUE")),
        Category("Backend", ("NODE_JS", "EXPRESS", "DJANGO", "FLASK", "FASTAPI", "SPRING_BOOT")),
        Category(
            "Database",
            ("SQL", "POSTGRESQL", "MYSQL", "MARIADB", "SQLITE", "SQL_SERVER",
             "ORACLE", "MONGODB", "CASSANDRA", "DYNAMODB"),
        ),
        Category("API", ("REST_API",), optional=True),
        Category("Version control", ("GIT", "GITHUB", "GITLAB", "BITBUCKET")),
    ),
)
