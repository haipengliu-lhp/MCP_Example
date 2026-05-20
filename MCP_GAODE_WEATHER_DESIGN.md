# Python MCP 高德天气 Client/Server 设计

## 目标

本项目实现一个 Python 3.11 版 MCP 示例系统：

- MCP Server 暴露高德地图天气查询工具。
- MCP Client 通过 `stdio` 调用本地 MCP Server。
- 天气数据源使用高德地图天气 API。
- 支持中文和常见英文城市输入。
- 查询结果统一输出中文。
- Server 保持标准 MCP stdio 形态，后续可接入 Claude Desktop、Codex 或其他 MCP Host。
- 新增 Web API 和浏览器页面，让网页也可以调用 MCP Server 的天气能力。

## 项目结构

```text
mcp-example/
  MCP_GAODE_WEATHER_DESIGN.md
  README.md
  requirements.txt
  .gitignore
  .env.example
  src/
    weather_server.py
    weather_client.py
    web_api.py
    gaode_weather_api.py
    city_resolver.py
    config.py
  web/
    index.html
  tests/
    test_gaode_weather_api.py
    test_city_resolver.py
    test_web_api.py
```

## 调用架构

### MCP Host 调用

Claude Desktop、Codex 或其他 MCP Host 可以直接按 stdio 方式启动 `weather_server.py`：

```text
MCP Host
  -> weather_server.py
  -> gaode_weather_api.py
  -> 高德地图天气 API
```

### 本地 Client 调用

`weather_client.py` 是本地开发和验证用的 MCP Client：

```text
weather_client.py
  -> MCP stdio
  -> weather_server.py
  -> 高德地图天气 API
```

### 网页调用

浏览器不能直接调用 stdio MCP Server，因此新增 `web_api.py` 作为 HTTP 桥接层：

```text
浏览器页面 web/index.html
  -> HTTP GET /api/weather
  -> FastAPI web_api.py
  -> weather_client.py
  -> MCP stdio
  -> weather_server.py
  -> 高德地图天气 API
```

这样网页调用仍然经过 MCP Server，不绕过现有 MCP 工具能力。

## MCP 工具接口

Server 暴露工具：`get_weather`

输入：

```json
{
  "city": "北京",
  "extensions": "base"
}
```

规则：

- `city` 必填，支持中文城市名和常见英文城市名，例如 `北京`、`Shanghai`。
- `extensions` 默认 `base`。
- `base` 查询实时天气。
- `all` 查询天气预报。
- 输出字段统一为中文。

实时天气输出示例：

```json
{
  "城市": "上海市",
  "省份": "上海",
  "天气": "晴",
  "温度": "26℃",
  "湿度": "62%",
  "风向": "东南",
  "风力": "≤3级",
  "发布时间": "2026-05-20 10:00:00"
}
```

## Web API 接口

新增 FastAPI 应用：`src/web_api.py`

接口：

```text
GET /
GET /api/weather?city=北京&extensions=base
```

规则：

- `/` 返回浏览器页面 `web/index.html`。
- `/api/weather` 接收 `city` 和 `extensions` 参数。
- `city` 不能为空，否则返回 HTTP 400 和中文错误。
- `extensions` 支持 `base` 和 `all`。
- Web API 内部调用 `weather_client.call_weather()`，再由 MCP Client 通过 stdio 调用 `weather_server.py`。
- MCP Server 返回错误时，Web API 转换为 HTTP 502 和中文错误。

启动示例：

```powershell
$env:GAODE_API_KEY="your_gaode_api_key_here"
.\.venv\Scripts\python.exe -m uvicorn src.web_api:app --reload --host 127.0.0.1 --port 8000
```

浏览器访问：

```text
http://127.0.0.1:8000
```

## 配置与安全

- API Key 通过环境变量 `GAODE_API_KEY` 提供。
- `.env.example` 只包含占位符。
- `.env` 被 `.gitignore` 排除，不提交真实密钥。
- Web API 也通过环境变量向 MCP Server 传递 `GAODE_API_KEY`，不在前端页面暴露真实密钥。
- 提交前需要检查 Git diff，确认没有真实 API Key。

## 模块职责

- `city_resolver.py`：将中文或常见英文城市名转换为高德可识别的中文城市名。
- `gaode_weather_api.py`：封装高德天气 API 调用、错误处理和中文输出格式转换。
- `weather_server.py`：注册 MCP 工具 `get_weather`，通过 stdio 运行。
- `weather_client.py`：本地开发示例 Client，启动 Server 并调用工具。
- `web_api.py`：HTTP 桥接层，让浏览器可以通过 Web API 调用 MCP Server。
- `web/index.html`：浏览器查询页面，调用 `/api/weather` 并展示中文天气结果。
- `config.py`：读取运行环境配置。

## 测试计划

- 城市解析测试：中文城市、常见英文城市、未知城市。
- 高德 API 测试：实时天气、天气预报、接口失败码。
- MCP 验收：Client 能通过 stdio 启动 Server 并调用 `get_weather`。
- Web API 测试：
  - `/` 能返回浏览器页面。
  - `/api/weather` 能返回中文天气 JSON。
  - 空城市返回 HTTP 400。
  - MCP 调用失败时返回中文错误。
- 安全检查：提交前扫描 staged diff，确认没有真实 API Key。

## Git 提交规则

实施完成后，AI 在以下条件满足时提交：

- 设计文档、代码、README、测试文件已完成。
- `.gitignore` 已排除 `.env`。
- 测试或手动验证已通过。
- Git diff 已确认不包含真实 API Key。
- 提交前明确提示：`现在准备执行 git commit`。

默认提交信息：

```text
feat: add web access for MCP Gaode weather server
```
