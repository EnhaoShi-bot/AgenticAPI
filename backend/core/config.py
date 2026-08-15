from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parents[1]

ENV_FILE_PATH = BASE_DIR / 'backend/.env'
print(f"[DEBUG] BASE_DIR: {BASE_DIR}")
print(f"[DEBUG] ENV_FILE_PATH: {ENV_FILE_PATH}")
print(f"[DEBUG] ENV_FILE_EXISTS: {ENV_FILE_PATH.exists()}")

# 尝试手动读取 .env 内容，检查编码问题
if ENV_FILE_PATH.exists():
    try:
        with open(ENV_FILE_PATH, 'r', encoding='utf-8') as f:
            print(".ENV文件已成功读取")
    except Exception as e:
        print(f"[DEBUG] READ_ERROR: {e}")
else:
    print("[DEBUG] .env file not found!")


class Settings(BaseSettings):
    """配置类"""
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding='utf-8',
    )

    MYSQL_HOST : str
    MYSQL_PORT: int
    MYSQL_USER : str
    MYSQL_PASSWORD : str
    MYSQL_DATABASE: str

    DEBUG : bool

    @property
    def MYSQL_URL(self) -> str:
        return f"mysql+asyncmy://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

setting = Settings()