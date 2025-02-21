from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

model_config = SettingsConfigDict(extra="allow", env_file=".env")


class APISettings(BaseSettings):
    HOST: str
    PORT: int

    model_config = model_config


class AgentSettings(BaseSettings):
    OPENAI_API_KEY: SecretStr
    OPENAI_MODEL: str
    OPENAI_MODEL_MINI: str
    MAX_HISTORY_LENGTH: int
    INVENTORY_DATA_N8N_WEBHOOK: str
    SALES_DATA_N8N_WEBHOOK: str

    model_config = model_config


agent_cfg = AgentSettings()
api_cfg = APISettings()
