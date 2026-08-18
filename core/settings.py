# ╔════════════════════════════════════════════════════════════╗
# ║ 🚚 IMPORTS
# ╚════════════════════════════════════════════════════════════╝

from typing import List, ClassVar
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# ╔════════════════════════════════════════════════════════════╗
# ║ ⚙️ CONFIG
# ╚════════════════════════════════════════════════════════════╝
class Settings(BaseSettings):
    # ═════════════════════ APP ═════════════════════
    APP_NAME: str = "Predict Churn"
    DESCRIPTION: str = ""
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8000",
        "http://localhost:127.0.0.1",
    ]
    DEMO_MODE: bool = False

    # ═════════════════════ PATH ═════════════════════
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parents[1]
    BASELINE_PATH: ClassVar[Path] = BASE_DIR / "models" / "baseline_model_bis.joblib"

    # ═════════════════════ USER ═════════════════════
    SECRET_KEY: str = ""
    USERNAME: str = "admin"

    # ═════════════════════ TOKEN ═════════════════════
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ACCESS_TOKEN_EXPIRE_DAYS: int = 1
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ═════════════════════ CONFIG ═════════════════════
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
