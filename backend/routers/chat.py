"""
聊天API路由
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
import json
import os
import sys
from typing import Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rag import RagService

router = APIRouter()

_rag_service = None

def get_rag_service():
    """获取RAG服务实例（延迟初始化）"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RagService()
    return _rag_service

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.websocket("/chat/stream")
async def chat_stream(websocket: WebSocket):
    """流式聊天WebSocket接口"""
    await websocket.accept()

    try:
        conversation_chain = get_rag_service().get_conversation_chain()

        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            message = message_data.get("message")
            session_id = message_data.get("session_id", "default")

            if not message:
                await websocket.send_text(json.dumps({"error": "Message is required"}))
                continue

            session_config = {"configurable": {"session_id": session_id}}

            try:
                # 使用流式输出
                full_response = ""
                async for chunk in conversation_chain.astream(
                    {"input": message},
                    config=session_config
                ):
                    # chunk可能是字符串或字典，需要处理
                    chunk_str = chunk if isinstance(chunk, str) else str(chunk)
                    if chunk_str:
                        # 发送流式数据块
                        await websocket.send_text(json.dumps({
                            "type": "chunk",
                            "content": chunk_str,
                            "session_id": session_id
                        }))
                        full_response += chunk_str
                
                # 发送完成信号
                await websocket.send_text(json.dumps({
                    "type": "done",
                    "response": full_response,
                    "session_id": session_id
                }))

            except Exception as e:
                import traceback
                error_detail = traceback.format_exc()
                print(f"流式输出错误: {error_detail}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": str(e)
                }))

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """非流式聊天POST接口"""
    try:
        conversation_chain = get_rag_service().get_conversation_chain()
        session_config = {"configurable": {"session_id": request.session_id}}

        result = conversation_chain.invoke(
            {"input": request.message},
            config=session_config
        )

        return ChatResponse(response=result, session_id=request.session_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))