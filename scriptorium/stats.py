"""Re-export of the recipe statistics (recipes import them as `scriptorium_stats`, see recipelib/)."""
from .recipelib.scriptorium_stats import *  # noqa: F401,F403
from .recipelib.scriptorium_stats import ci95, cohens_dz, diff_ci95, mean, paired_p, paired_t_p, sd, sem, wins  # noqa: F401,E501
