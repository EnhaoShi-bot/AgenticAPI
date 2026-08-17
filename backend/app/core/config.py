"""应用配置：基于 pydantic-settings 从 backend/.env 读取"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / '.env'
DATA_DIR = BASE_DIR / 'data'  # 运行期数据目录（敏感凭证 / 调试快照），已加入 .gitignore


class MysqlSettings(BaseSettings):
    """配置类"""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding='utf-8',
    )

    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    DEBUG: bool

    # 阶跃星辰 ASR 服务密钥（模型工坊语音输入用，可选；未配置时语音接口返回 503）
    STEPFUN_API_KEY: str = ''

    @property
    def MYSQL_URL(self) -> str:
        return f"mysql+asyncmy://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"


setting = MysqlSettings()
