import sys
from pathlib import Path

# 把 backend 目录加入 sys.path，解决 IDE 标红和运行时导入问题
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.config import setting  # 现在 IDE 和运行时都能正确解析
from sqlalchemy.orm import Session
from backend.db.mysql_tables import BaseModel  # 【关键】导入 BaseModel 会自动注册所有继承它的表定义到 metadata 中
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,async_session

engine = create_async_engine(
    setting.MYSQL_URL, # 数据库连接字符串
    pool_pre_ping=True, # 连接池预检查
    echo=setting.DEBUG, # 输出数据库语句
    pool_size=10, # 连接池大小
    max_overflow=10, # 最大溢出连接数

)

asyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine # 绑定异步引擎
)


async def init_database():
    """
    初始化数据库表结构
    - 如果表不存在，则自动创建
    - 如果表已存在，则跳过（不会重复创建或修改现有表）

    【工作原理】
    1. BaseModel.metadata 中存储了所有继承 BaseModel 的表定义（如 ModelsTable、ChannelsTable）
    2. create_all() 会遍历 metadata 中的所有表，执行 CREATE TABLE IF NOT EXISTS
    3. 新增表只需在 mysql_tables.py 中定义新类并继承 BaseModel，无需修改此函数
    """
    try:
        # 使用 run_sync() 在异步引擎上执行同步的 create_all
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)
        print("数据库表初始化完成（已存在的表会被跳过）")
    except Exception as e:
        print(f"数据库表初始化失败：{e}")
        raise


def orm_crud_demo():
    """
    ORM 风格的 CRUD 示例，保留作为学习参考。
    需要导入 ModelsTable 才能使用：
        from backend.app.db.mysql_tables import ModelsTable
        from sqlalchemy import update, select, delete
    """
    from backend.db.mysql_tables import ModelsTable
    from sqlalchemy import update, select, delete

    agentic_db = asyncSessionLocal()

    try:
        new_model = ModelsTable(
            name="gpt-3.5-turbo",
            label="GPT-3.5 Turbo",
            description="基于GPT-3.5的Turbo模型，支持对话和任务完成",
            is_request_mode=0,
            per_request_price=0.002,
            input_price=0.001,
            cache_price=0.001,
            output_price=0.001,
            model_group="free",
            is_pin=0,
            is_log=0,
            status=1,
            channels="['channel1','channel2','channel3']",
            context_length=128000,
            max_tokens=10240,
            support_vision=0,
        )

        # 增
        agentic_db.add(new_model)
        agentic_db.flush()
        print("=" * 60)
        print(f"新增模型成功，模型ID：{new_model.id}，模型名称：{new_model.name}")
        print("=" * 60)
        agentic_db.commit()

        # 改
        agentic_db.execute(
            update(ModelsTable)
            .where(ModelsTable.name == "gpt-3.5-turbo")
            .values(name="gpt-3.6-turbo")
        )
        agentic_db.flush()
        print("=" * 60)
        print(f"修改模型成功，模型ID：{new_model.id}，模型名称：{new_model.name}")
        print("=" * 60)
        agentic_db.commit()

        # 查单条
        the_model = agentic_db.scalars(
            select(ModelsTable).where(ModelsTable.name == "deepseek-v4-flash")
        ).first()
        if the_model:
            print("=" * 60)
            print(f"查询到 {the_model.name} 的模型输入价格是 {the_model.input_price}")
            print("=" * 60)

        # 查全部
        all_models = agentic_db.scalars(select(ModelsTable)).all()
        print("=" * 60)
        for model in all_models:
            print(f"模型ID：{model.id}，模型名称：{model.name}")
        print("=" * 60)

        # 删
        agentic_db.execute(
            delete(ModelsTable).where(ModelsTable.name == "gpt-3.6-turbo")
        )
        agentic_db.flush()
        print("=" * 60)
        print(f"删除模型成功，模型ID：{new_model.id}，模型名称：{new_model.name}")
        print("=" * 60)
        agentic_db.commit()

    except Exception as e:
        print(f"数据库操作失败：{e}")
        agentic_db.rollback()
        raise

    finally:
        agentic_db.close()


def raw_sql_crud_demo():
    """
    原生 SQL 风格的 CRUD 示例。
    """
    agentic_db = asyncSessionLocal()

    try:
        # 增
        result = agentic_db.execute(
            text("""
                 INSERT INTO llm_models
                 (name, label, description, is_request_mode, per_request_price,
                  input_price, cache_price, output_price, model_group, is_pin,
                  is_log, status, channels, context_length, max_tokens, support_vision)
                 VALUES (:name, :label, :description, :is_request_mode, :per_request_price,
                         :input_price, :cache_price, :output_price, :model_group, :is_pin,
                         :is_log, :status, :channels, :context_length, :max_tokens, :support_vision)
                 """),
            {
                "name": "gpt-3.5-turbo",
                "label": "GPT-3.5 Turbo",
                "description": "基于GPT-3.5的Turbo模型，支持对话和任务完成",
                "is_request_mode": 0,
                "per_request_price": 0.002,
                "input_price": 0.001,
                "cache_price": 0.001,
                "output_price": 0.001,
                "model_group": "free",
                "is_pin": 0,
                "is_log": 0,
                "status": 1,
                "channels": "['channel1','channel2','channel3']",
                "context_length": 128000,
                "max_tokens": 10240,
                "support_vision": 0,
            },
        )
        agentic_db.flush()
        new_id = result.lastrowid
        print("=" * 60)
        print(f"新增模型成功，模型ID：{new_id}")
        print("=" * 60)
        agentic_db.commit()

        # 改
        agentic_db.execute(
            text("UPDATE llm_models SET name = :new_name WHERE name = :old_name"),
            {"new_name": "gpt-3.6-turbo", "old_name": "gpt-3.5-turbo"},
        )
        agentic_db.flush()
        print("=" * 60)
        print(f"修改模型成功，gpt-3.5-turbo -> gpt-3.6-turbo")
        print("=" * 60)
        agentic_db.commit()

        # 查单条
        row = agentic_db.execute(
            text("SELECT * FROM llm_models WHERE name = :name"),
            {"name": "deepseek-v4-flash"},
        ).mappings().first()
        if row:
            print("=" * 60)
            print(f"查询到 {row['name']} 的模型输入价格是 {row['input_price']}")
            print("=" * 60)

        # 查全部
        rows = agentic_db.execute(
            text("SELECT id, name FROM llm_models")
        ).mappings().all()
        print("=" * 60)
        for row in rows:
            print(f"模型ID：{row['id']}，模型名称：{row['name']}")
        print("=" * 60)

        # 删
        agentic_db.execute(
            text("DELETE FROM llm_models WHERE name = :name"),
            {"name": "gpt-3.6-turbo"},
        )
        agentic_db.flush()
        print("=" * 60)
        print(f"删除模型成功，gpt-3.6-turbo")
        print("=" * 60)
        agentic_db.commit()

    except Exception as e:
        print(f"数据库操作失败：{e}")
        agentic_db.rollback()
        raise

    finally:
        agentic_db.close()


# 依赖项，获取数据库会话
async def get_db():
    async with asyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
# 不需要手动 finally + session.close
# async with 上下文管理器退出时自动关闭 AsyncSession

if __name__ == '__main__':
    """
    运行命令：python -m backend.app.db.session
    """
    raw_sql_crud_demo()