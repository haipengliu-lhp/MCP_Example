# MCP 高德天气 Client/Server

这是一个 Python 3.11 版 MCP 示例项目。Server 提供高德地图天气查询工具，Client 通过 `stdio` 调用本地 Server。项目还提供一个 FastAPI Web 桥接层，让浏览器页面可以通过 HTTP 调用 MCP Server 的天气能力。

## 安装

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

配置环境变量：

```powershell
$env:GAODE_API_KEY="your_gaode_api_key_here"
```

也可以在你自己的 shell、Web 服务进程或 MCP Host 配置中注入 `GAODE_API_KEY`。不要把真实 API Key 提交到 Git。

## 网页调用

启动 Web API：

```powershell
$env:GAODE_API_KEY="your_gaode_api_key_here"
.\.venv\Scripts\python.exe -m uvicorn src.web_api:app --reload --host 127.0.0.1 --port 8000
```

浏览器访问：

```text
http://127.0.0.1:8000
```

网页调用链：

```text
web/index.html
  -> GET /api/weather
  -> src/web_api.py
  -> src/weather_client.py
  -> MCP stdio
  -> src/weather_server.py
  -> 高德地图天气 API
```

HTTP API 示例：

```text
GET http://127.0.0.1:8000/api/weather?city=北京&extensions=base
GET http://127.0.0.1:8000/api/weather?city=Shanghai&extensions=all
```

## 本地 MCP Client 调用

查询实时天气：

```powershell
python .\src\weather_client.py 北京
python .\src\weather_client.py Shanghai
```

查询天气预报：

```powershell
python .\src\weather_client.py 北京 --extensions all
```

## MCP Server

Server 启动命令：

```powershell
python .\src\weather_server.py
```

MCP 工具名：`get_weather`

输入示例：

```json
{
  "city": "北京",
  "extensions": "base"
}
```

## Claude Desktop 接入示例

把命令、参数和环境变量按你的本机路径放入 Claude Desktop MCP 配置：

```json
{
  "mcpServers": {
    "gaode-weather": {
      "command": "python",
      "args": ["D:\\ai-example\\mcp-example\\src\\weather_server.py"],
      "env": {
        "GAODE_API_KEY": "your_gaode_api_key_here"
      }
    }
  }
}
```

## Codex 或其他 MCP Host 接入

这个 Server 不依赖 Claude Desktop 或 Codex 的专有能力。任何支持 MCP stdio Server 的 Host 都可以使用相同三项配置：

- `command`: `python`
- `args`: `["D:\\ai-example\\mcp-example\\src\\weather_server.py"]`
- `env.GAODE_API_KEY`: 你的高德地图 API Key

## 测试

```powershell
python -m unittest discover -s tests
```

测试不会访问真实高德 API，网络响应通过注入的 fake HTTP 函数模拟。Web API 测试会 mock MCP 调用，真实网页验收可以启动 uvicorn 后访问本地页面。
