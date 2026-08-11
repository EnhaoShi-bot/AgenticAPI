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

engine = create_engine(
    setting.MYSQL_URL,
    pool_pre_ping=True,
    echo=setting.DEBUG
)

sessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def orm_crud_demo():
    """
    ORM 风格的 CRUD 示例，保留作为学习参考。
    需要导入 ModelsTable 才能使用：
        from backend.app.db.mysql_tables import ModelsTable
        from sqlalchemy import update, select, delete
    """
    from backend.db.mysql_tables import ModelsTable
    from sqlalchemy import update, select, delete

    agentic_db = sessionLocal()

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
    agentic_db = sessionLocal()

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


# 获取数据库会话
def get_db() -> Session:
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == '__main__':
    """
    运行命令：python -m backend.app.db.session
    """
    raw_sql_crud_demo()
