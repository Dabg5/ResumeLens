from .base import Category, Profile
from .data_engineer import DATA_ENGINEER
from .devops_engineer import DEVOPS_ENGINEER
from .fullstack import FULL_STACK
from .ml_engineer import ML_ENGINEER

PROFILES: dict[str, Profile] = {
    p.key: p for p in (FULL_STACK, ML_ENGINEER, DEVOPS_ENGINEER, DATA_ENGINEER)
}

__all__ = ["Category", "Profile", "PROFILES", "FULL_STACK", "ML_ENGINEER",
           "DEVOPS_ENGINEER", "DATA_ENGINEER"]
