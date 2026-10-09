from .base import Category, Profile

ML_ENGINEER = Profile(
    key="ml_engineer",
    name="Machine Learning Engineer",
    description=(
        "Predictive/learning-based systems: Python, a data-processing library, "
        "a machine-learning framework, SQL and Git."
    ),
    automaton_type="NFA",
    categories=(
        Category("Language", ("PYTHON",)),
        Category("Data processing", ("PANDAS", "NUMPY")),
        Category("ML framework", ("SCIKIT_LEARN", "TENSORFLOW", "PYTORCH", "KERAS")),
        Category("Database", ("SQL", "POSTGRESQL", "MYSQL")),
        Category("Version control", ("GIT",)),
    ),
)
