"""riasec-co: Bayesian adaptive RIASEC quiz engine with Colombian SNIES data."""

from riasec_co.quiz import Quiz
from riasec_co.data import Programs, load_items, load_mapping
from riasec_co.recommender import recommend

__all__ = ["Quiz", "Programs", "load_items", "load_mapping", "recommend"]
__version__ = "0.1.0"
