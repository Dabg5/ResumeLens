from .base import Category, Profile

DEVOPS_ENGINEER = Profile(
    key="devops_engineer",
    name="DevOps Engineer",
    description=(
        "Delivery and infrastructure: scripting, containers, orchestration, "
        "CI/CD, a cloud provider, optional infrastructure as code and Git."
    ),
    automaton_type="ε-NFA",
    categories=(
        Category("Scripting", ("PYTHON", "BASH")),
        Category("Containers", ("DOCKER",)),
        Category("Orchestration", ("KUBERNETES",)),
        Category("CI/CD", ("GITHUB_ACTIONS", "JENKINS", "GITLAB_CI")),
        Category("Cloud", ("AWS", "AZURE", "GCP")),
        Category("Infrastructure as code", ("TERRAFORM", "ANSIBLE"), optional=True),
        Category("Version control", ("GIT", "GITHUB", "GITLAB", "BITBUCKET")),
    ),
)
