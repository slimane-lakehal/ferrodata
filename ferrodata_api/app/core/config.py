from pathlib import Path
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).parent.parent.parent / ".env"
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

class Settings(BaseSettings):
    """
    Application settings
    """
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        )
        
    # API configuration
    api_version: str = " "
    environment: str = "development"

    # Database configuration
    db_path: str = "ferrodata.duckdb"

    @computed_field
    def api_prefix(self) -> str:
        return f"/api/{self.api_version}"

    @computed_field
    @property
    def db_absolute_path(self) -> str:
        p = Path(self.db_path)
        return p if p.is_absolute() else PROJECT_ROOT / p

settings = Settings()


if __name__ == "__main__":
    print(settings)