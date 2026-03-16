# 期末复习资料检索增强系统 (RAG)

基于 FastAPI + React 的前后端分离 RAG 项目，支持文档入库、语义检索、多轮会话与流式回答，面向“复习资料问答”场景。

## 1. 项目亮点

- 文档上传与管理：支持 `.txt` / `.pdf` / `.docx` 批量上传、列表查看、按文档删除。
- 混合检索：向量检索 + BM25 融合，提高召回效果与答案相关性。
- 对话记忆：会话级历史持久化，支持多会话切换和删除。
- 流式问答：WebSocket 增量输出，前端实时渲染回复内容。
- 工程化结构：前后端分离，便于本地开发、团队协作和后续扩展。

## 2. 技术栈

### 后端

- FastAPI / Uvicorn
- LangChain
- Chroma (本地向量库)
- DashScopeEmbeddings + ChatTongyi (通义千问)
- python-dotenv

### 前端

- React
- react-icons
- 原生 CSS

## 3. 目录结构

```text
.
├── backend/
│   ├── main.py                # FastAPI 入口
│   ├── rag.py                 # RAG 对话链构建
│   ├── knowledge_base.py      # 文档入库与向量化
│   ├── vector_stores.py       # 向量检索与混合检索
│   ├── file_history_store.py  # 会话历史存储
│   ├── config_data.py         # 可调配置
│   ├── requirements.txt       # 后端依赖
│   └── routers/
│       ├── chat.py            # 聊天接口
│       ├── upload.py          # 上传/文档管理接口
│       └── sessions.py        # 会话管理接口
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   └── components/
│   └── package.json
├── data/                      # 示例资料（可按需保留）
└── README.md
```

## 4. 环境要求

- Python 3.8+
- Node.js 16+（建议 18 LTS）
- npm 8+
- DashScope API Key

## 5. 快速开始

### 5.1 克隆并进入项目

```bash
git clone <your-repo-url>
cd RagForExm
```

### 5.2 配置环境变量

在项目根目录创建 `.env`：

```env
DASHSCOPE_API_KEY=your_actual_api_key_here
# 兼容字段（可选）
# API_KEY=your_actual_api_key_here
```

> 后端启动时会校验 `DASHSCOPE_API_KEY` 或 `API_KEY`，若未配置会直接退出。

### 5.3 启动后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

后端默认地址：`http://localhost:8000`

### 5.4 启动前端

新开一个终端：

```bash
cd frontend
npm install
npm start
```

前端默认地址：`http://localhost:3000`

## 6. 使用流程

1. 打开“知识库管理”，上传复习资料（支持拖拽多文件）。
2. 在“复习问答”输入问题，系统通过知识库检索后生成回答。
3. 在“会话管理”查看历史会话，支持切换与删除。

## 7. API 概览

### HTTP 接口

- `GET /`：服务健康返回。
- `POST /api/upload`：上传单个文档。
- `POST /api/upload/batch`：批量上传文档。
- `GET /api/documents`：获取已入库文档列表。
- `DELETE /api/documents/{document_id}`：删除指定文档。
- `GET /api/sessions`：获取会话列表。
- `DELETE /api/sessions/{session_id}`：删除指定会话。
- `POST /api/chat`：非流式聊天。

### WebSocket

- `WS /api/chat/stream`：流式聊天，前端按 chunk 增量接收模型回复。

## 8. 核心配置说明

配置文件：`backend/config_data.py`

- `persist_directory`：向量库存储目录（默认 `./chroma_db`）。
- `chat_history_path`：会话历史目录（默认 `./chat_history`）。
- `chunk_size` / `chunk_overlap`：文本切片参数。
- `similarity_threshold`：检索返回文档数量。
- `bm25_weight` / `vector_weight`：混合检索权重。
- `ensemble_k`：融合检索返回数量。
- `embedding_model_name` / `chat_model_name`：模型名称。

## 9. `.gitignore` 策略说明

已按“可提交源码 + 本地运行产物不提交”原则配置，默认忽略：

- Python 缓存与构建产物（`__pycache__`、`*.pyc`、`dist/` 等）。
- 虚拟环境目录（`venv/`、`.venv/`）。
- 本地数据库与向量库（`*.db`、`chroma_db/`、`chat_history/`）。
- 前端依赖和构建产物（`node_modules/`、`frontend/build/`）。
- 日志、覆盖率、临时文件和 IDE 配置文件。

这样可以避免将不必要文件推送到远程仓库，减小仓库体积并提高协作可读性。

## 10. 常见问题

### 10.1 启动时报错“未找到 DASHSCOPE_API_KEY”

- 确认项目根目录存在 `.env`。
- 确认键名正确：`DASHSCOPE_API_KEY=...`。

### 10.2 前端无法请求后端

- 确认后端已启动在 `8000` 端口。
- 检查是否被本机代理、杀毒或防火墙拦截。
- 当前 CORS 默认允许 `http://localhost:3000`。

### 10.3 上传后问答效果不理想

- 检查资料内容是否可被正确提取（PDF 扫描件可能无文本层）。
- 调整 `chunk_size/chunk_overlap` 与混合检索权重。
- 先上传结构清晰的文本样本验证链路。

## 11. 提交流程建议

```bash
git add .gitignore README.md
git commit -m "chore: refine gitignore and expand README"
git push
```

## 12. 许可证

本项目当前用于学习与实践，若需开源发布，建议补充标准开源许可证（如 MIT）。

