"""
会话管理API路由
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
import sys
from typing import List, Optional

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config_data as config

router = APIRouter()

class SessionInfo(BaseModel):
    session_id: str
    message_count: int

class SessionsResponse(BaseModel):
    sessions: List[SessionInfo]

@router.get("/sessions", response_model=SessionsResponse)
async def get_sessions():
    """获取所有会话列表"""
    try:
        storage_path = config.chat_history_path
        sessions = []

        if os.path.exists(storage_path):
            for filename in os.listdir(storage_path):
                if filename.endswith('.json'):
                    session_id = filename[:-5]  # 移除.json后缀
                    file_path = os.path.join(storage_path, filename)

                    # 计算消息数量
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            message_count = len(data.get('messages', []))
                    except:
                        message_count = 0

                    sessions.append(SessionInfo(
                        session_id=session_id,
                        message_count=message_count
                    ))

        return SessionsResponse(sessions=sessions)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除指定会话"""
    try:
        storage_path = config.chat_history_path
        file_path = os.path.join(storage_path, f"{session_id}.json")

        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": f"Session {session_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))