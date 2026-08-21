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
        extra='ignore', # 忽略 .env 中未定义的变量
    )

    MYSQL_HOST: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    DEBUG: bool

    @property
    def MYSQL_URL(self) -> str:
        return f"mysql+asyncmy://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"


class ServerSettings(BaseSettings):
    """服务运行配置：监听地址 / 端口 / 对外公开地址"""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding='utf-8',
        extra='ignore', # 忽略 .env 中未定义的变量
    )

    # 后端监听地址与端口（python -m app.main 启动时生效）
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 2027
    # 对外公开访问地址（部署到公网时改为真实 URL）：
    # 模型拨测自调用、GET /site/info 下发给前端展示的中转接口地址都用它
    PUBLIC_BASE_URL: str = "http://localhost:2027"

    @property
    def RELAY_BASE_URL(self) -> str:
        """对外中转接口基地址（OpenAI 兼容），已去掉尾部斜杠便于拼接路径"""
        return self.PUBLIC_BASE_URL.rstrip('/') + '/v1'


class AgentSettings(BaseSettings):
    """Agent 能力专用配置：直连 StepFun，不经渠道/模型表，不计费不记日志"""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding='utf-8',
        extra='ignore', # 忽略 .env 中未定义的变量
    )

    # StepFun OpenAI 兼容对话端点
    AGENT_BASE_URL: str = ""
    # StepFun ASR 兼容端点
    ASR_BASE_URL: str = ""
    # StepFun 密钥（与工坊语音 ASR 共用同一把，不另配一份）
    STEPFUN_API_KEY: str = ""
    # Agent 标题模型（默认使用 StepFun 模型）
    AGENT_TITLE_MODEL: str = ""


agent_setting = AgentSettings()
setting = MysqlSettings()
server_setting = ServerSettings()
