# AgenticCLI / MCP 封装构想

> 记录日期：2026-08-17 ｜ 状态：构想（未实施）
> 前置产物：用户级 skill `agenticapi-ops`（位于 `C:\Users\18957\.zcode\skills\agenticapi-ops\`），已通过隔离环境全链路实测

## 现状

当前已有一个可用的最小闭环：skill（`SKILL.md` 运维纪律 + 命令速查）+ 零依赖 CLI 脚本（`scripts/agenticapi.py`，纯标准库），覆盖渠道与模型两类资源的 `list / get / create / update / delete` 及 `login / whoami`。

实现过程中已解决并封装好的难点（后续无论哪个方向都直接复用）：

- 登录与 token 缓存（`~/.agenticapi/session.json`，只存 token 不存密码）
- 401 自动重登：`user_token` 表每用户仅一条记录，任何端重新登录会顶掉旧令牌
- 中文渠道名的 URL 路径编码
- `PUT /channels` 请求体必含 `channelName`（定位键，缺失 422）的自动补全
- 统一 `{code, message, data}` 响应解析与业务错误信息透传（400/401/403/404/422）
- `--json / --file / --set k=v` 三种请求体输入方式

凭证机制：复用平台自身用户体系——管理员账号密码（环境变量 `AGENTICAPI_ADMIN_USER/PASSWORD` 或命令行参数）→ `POST /user/login` → uuid4 令牌（正式账号 30 天）→ 后续请求自动携带 `Authorization: Bearer <token>`。

## 演进方向 A：正式 CLI（类似飞书 CLI）

**形态**：pip 包 + `pyproject.toml` console_scripts 入口，`uv tool install` / `pipx install` 后全局可用 `agentic` 命令；增加 `~/.agenticapi/config.toml` 持久化 `base_url` 等非敏感配置。

**工作量**：小（半天内）。核心逻辑已在 `agenticapi.py` 中验证，剩下是工程包装；扩展更多资源（用户、密钥、日志）时每类资源只是新增一组 subparser + 端点映射。

**优点**：人与 agent 通用、零运行时依赖、无常驻进程；可与 skill 共存（SKILL.md 改为调用正式 CLI 即可）。

**缺点**：只解决"执行"，agent 侧仍需 skill 之类的说明书承载运维纪律（写前先读、删除确认、影响面评估）。

## 演进方向 B：MCP Server

**形态**：FastMCP 封装，每个运维操作注册为一个 tool（`login` / `list_channels` / `create_model` / `update_model_pricing` ...），stdio 本地运行或 SSE 远程部署。

**工作量**：小（起步 1-2 小时）。直接复用 `agenticapi.py` 的请求层，每个函数加一行 `@mcp.tool()` 装饰器并补写工具描述。

**优点**：协议标准，ZCode / Claude / Cursor 等 MCP 客户端即插即用，不绑定 skill 机制；工具描述自带触发语义，agent 无需额外说明书即可发现能力。

**缺点**：常驻进程 + 客户端侧配置；运维纪律只能写进工具描述，对 agent 的约束力弱于 skill 正文；远程 SSE 形态需要额外考虑鉴权边界。

## 对比与建议

| 维度 | A：正式 CLI | B：MCP Server |
| --- | --- | --- |
| 使用方 | 人 + agent（任意） | 任意 MCP 客户端的 agent |
| 运行形态 | 按需执行，无常驻 | 常驻进程 |
| agent 触发方式 | 需 skill/说明书引导 | 协议内置工具发现 |
| 运维纪律承载 | skill 正文（约束力强） | 工具描述（约束力弱） |
| 分发 | PyPI / 私有 git | PyPI / npx / 私有部署 |

建议：**MCP 优先**。本项目定位就是"基于 Agent 的 API 中转站"，运维工具面向 agent 分发是主诉求，MCP 的跨客户端即插即用最契合；CLI 可作为附属同步产出（同一套请求层，两种外壳），供人工排障时在终端直接使用。无论哪个方向，均沿用现有凭证与 token 缓存约定，密码不落盘。

## 待决事项

- [ ] 是否扩展到渠道/模型以外的资源（用户管理、密钥、调用日志），还是保持最小范围
- [ ] MCP 形态选择：本地 stdio（无需鉴权）还是远程 SSE（需加访问鉴权）
- [ ] 分发渠道：私有 git / 内部源 / PyPI 公开发布
- [ ] 若引入 `config.toml`，密码是继续只走环境变量，还是允许存文件（需权衡文件权限与便利性）
