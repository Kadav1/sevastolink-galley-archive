# Import all ORM models so SQLAlchemy can resolve FK references across modules.
from src.models.recipe import Recipe, RecipeIngredient, RecipeNote, RecipeSource, RecipeStep  # noqa: F401
from src.models.intake import CandidateIngredient, CandidateStep, IntakeJob, StructuredCandidate  # noqa: F401
from src.models.media import AIJob, MediaAsset  # noqa: F401
from src.models.settings import SettingEntry  # noqa: F401