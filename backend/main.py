"""
FastAPI后端应用入口
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, upload, sessions

def check_environment():
    """检查必要的环境变量"""
    import dotenv
    dotenv.load_dotenv()

    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        print("❌ 错误: 未找到 DASHSCOPE_API_KEY 或 API_KEY 环境变量")
        print("请在项目根目录创建 .env 文件，并添加以下内容:")
        print("DASHSCOPE_API_KEY=your_actual_api_key_here")
        print("然后重新启动服务")
        sys.exit(1)

    os.environ["DASHSCOPE_API_KEY"] = api_key
    print("✅ API Key 配置成功")

check_environment()

app = FastAPI(title="期末复习资料检索增强系统 API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])

@app.get("/")
async def root():
    return {"message": "期末复习资料检索增强系统 API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)