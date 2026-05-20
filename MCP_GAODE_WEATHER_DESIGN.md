# Python MCP 高德天气 Client/Server 设计

## 目标

本项目实现一个 Python 3.11 版 MCP 示例系统：

- MCP Server 暴露高德地图天气查询工具。
- MCP Client 通过 `stdio` 调用本地 MCP Server。
- 天气数据源使用高德地图天气 API。
- 支持中文和常见英文城市输入。
- 查询结果统一输出中文。
- Server 保持标准 MCP stdio 形态，后续可接入 Claude Desktop、Codex 或其他 MCP Host。

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
    gaode_weather_api.py
    city_resolver.py
    config.py
  tests/
    test_gaode_weather_api.py
    test_city_resolver.py
```

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

## 配置与安全

- API Key 通过环境变量 `GAODE_API_KEY` 提供。
- `.env.example` 只包含占位符。
- `.env` 被 `.gitignore` 排除，不提交真实密钥。
- 提交前需要检查 Git diff，确认没有真实 API Key。

## 模块职责

- `city_resolver.py`：将中文或常见英文城市名转换为高德可识别的中文城市名。
- `gaode_weather_api.py`：封装高德天气 API 调用、错误处理和中文输出格式转换。
- `weather_server.py`：注册 MCP 工具 `get_weather`，通过 stdio 运行。
- `weather_client.py`：本地开发示例 Client，启动 Server 并调用工具。
- `config.py`：读取运行环境配置。

## Git 提交规则

实施完成后，AI 在以下条件满足时提交：

- 设计文档、代码、README、测试文件已完成。
- `.gitignore` 已排除 `.env`。
- 测试或手动验证已通过。
- Git diff 已确认不包含真实 API Key。
- 提交前明确提示：`现在准备执行 git commit`。

默认提交信息：

```text
feat: add Python MCP Gaode weather client and server
```
