"""CRUD 通用工具"""


def build_set_clause(update_dict: dict) -> str:
    """构建动态 UPDATE 的 SET 子句，如 'a = :a, b = :b'"""
    return ", ".join(f"{key} = :{key}" for key in update_dict.keys())
