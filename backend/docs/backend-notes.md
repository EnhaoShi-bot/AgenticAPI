http请求分类：
- get：获取资源
- post：创建资源
- put：更新资源
- delete：删除资源


后端查询数据库有两种方式：
- 执行原始 SQL 语句
- 使用 SQLAlchemy 的 ORM 模型（Object-Relational Mapping），或其他 ORM 框架，包括java等其他后端语言也存在ORM框架


http请求里面有两种传参方式：
- 路径参数：在URL中直接包含参数值，例如：/models/{model_name}
- 查询参数：在URL中使用 ? 符号分隔，例如：/models/query?model_name=deepseek-v4-flash
