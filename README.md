# 期末复习资料检索增强系统 (RAG)

基于检索增强生成（RAG）技术的期末复习资料智能问答系统，帮助学生高效复习和检索学习资料。

## 项目简介

本项目是一个学习练手项目，采用前后端分离架构，使用 FastAPI + React 构建。系统支持上传复习资料文档，通过向量数据库进行语义检索，结合大语言模型提供智能问答服务。

## 技术栈

### 后端
- **FastAPI** - 现代、快速的 Web 框架
- **LangChain** - LLM 应用开发框架
- **Chroma** - 向量数据库
- **DashScope (通义千问)** - 大语言模型和嵌入模型
- **Python 3.8+**

### 前端
- **React** - UI 框架
- **React Icons** - 图标库
- **CSS3** - 样式设计

## 功能特性

- 📚 **知识库管理** - 支持上传 .txt、.pdf、.docx 格式的复习资料
- 🔍 **智能检索** - 基于向量检索和 BM25 的混合检索策略
- 💬 **智能问答** - 基于知识库的上下文感知问答
- 📝 **会话管理** - 支持多会话历史记录管理
- 🎨 **简洁界面** - 现代化、简洁的用户界面

## 项目结构

```
.
├── backend/              # 后端代码
│   ├── routers/         # API 路由
│   ├── chroma_db/        # 向量数据库存储
│   ├── chat_history/     # 会话历史存储
│   ├── main.py          # 应用入口
│   ├── rag.py           # RAG 服务
│   ├── knowledge_base.py # 知识库服务
│   └── config_data.py   # 配置文件
├── frontend/             # 前端代码
│   ├── src/
│   │   ├── components/  # React 组件
│   │   └── App.js       # 主应用
│   └── package.json
└── README.md
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- DashScope API Key

### 后端设置

1. 进入后端目录：
```bash
cd backend
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
在项目根目录创建 `.env` 文件：
```
DASHSCOPE_API_KEY=your_api_key_here
```

4. 启动后端服务：
```bash
python main.py
```

后端服务将在 `http://localhost:8000` 启动。

### 前端设置

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm start
```

前端应用将在 `http://localhost:3000` 启动。

## 使用说明

1. **上传资料**：在"知识库管理"页面上传复习资料文档
2. **开始问答**：在"复习问答"页面输入问题，系统会基于知识库内容回答
3. **管理会话**：在"会话管理"页面查看和管理历史会话

## 配置说明

主要配置在 `backend/config_data.py` 中：

- `chunk_size`: 文本分块大小（默认 1000）
- `chunk_overlap`: 分块重叠大小（默认 100）
- `similarity_threshold`: 向量检索返回文档数量（默认 2）
- `embedding_model_name`: 嵌入模型名称
- `chat_model_name`: 对话模型名称

## 注意事项

- 本项目为学习练手项目，不包含用户认证和安全功能
- 首次使用需要配置 DashScope API Key
- 建议在本地环境使用，生产环境需要额外配置

## 许可证

本项目仅供学习使用。

## 贡献

欢迎提交 Issue 和 Pull Request！

