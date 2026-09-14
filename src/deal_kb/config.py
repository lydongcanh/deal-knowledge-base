"""Central runtime configuration, loaded from environment variables / .env."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Typed application settings sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="DKB_", extra="ignore")

    # LadybugDB (embedded graph store)
    graph_db_path: Path = REPO_ROOT / "data" / "graph" / "deal_graph.lbdb"

    # AWS Bedrock
    aws_region: str = "ap-southeast-2"
    bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"


settings = Settings()
