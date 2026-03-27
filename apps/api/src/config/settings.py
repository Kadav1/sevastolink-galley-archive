from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo root is two levels up from apps/api/
REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    node_env: str = "development"
    api_port: int = 8000

    # Database — normalise the sqlite: prefix the .env.example uses
    database_url: str = f"sqlite:///{REPO_ROOT / 'data' / 'db' / 'galley.sqlite'}"

    # Data directories
    media_dir: Path = REPO_ROOT / "data" / "media"
    imports_dir: Path = REPO_ROOT / "data" / "imports"
    exports_dir: Path = REPO_ROOT / "data" / "exports"
    backups_dir: Path = REPO_ROOT / "data" / "backups"

    # LM Studio (optional). The model remains user-configurable; the repo's
    # recommended tested default for normalization is Qwen/Qwen2.5-7B-Instruct.
    lm_studio_enabled: bool = False
    lm_studio_base_url: str = "http://localhost:1234/v1"
    lm_studio_model: str = ""

    @property
    def sqlalchemy_database_url(self) -> str:
        url = self.database_url
        # Normalise bare `sqlite:./path` → `sqlite:///./path`
        if url.startswith("sqlite:") and not url.startswith("sqlite://"):
            url = "sqlite:///" + url[len("sqlite:"):]
        return url

    @property
    def db_path(self) -> Path:
        url = self.sqlalchemy_database_url
        # Strip scheme for path ops
        path_part = url.replace("sqlite:///", "")
        return Path(path_part).resolve()


settings = Settings()
