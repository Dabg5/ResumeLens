from .base import Category, Profile

DATA_ENGINEER = Profile(
    key="data_engineer",
    name="Data Engineer",
    description=(
        "Data pipelines: Python, SQL, a processing library, a workflow "
        "orchestrator, a data warehouse and Git."
    ),
    automaton_type="NFA",
    categories=(
        Category("Language", ("PYTHON",)),
        Category("Query language", ("SQL", "POSTGRESQL", "MYSQL")),
        Category("Processing", ("PANDAS", "PYSPARK")),
        Category("Orchestration", ("AIRFLOW",)),
        Category("Data warehouse", ("BIGQUERY", "SNOWFLAKE", "REDSHIFT")),
        Category("Version control", ("GIT",)),
    ),
)
