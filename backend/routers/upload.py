"""
文件上传API路由
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import sys
import io
from typing import Optional, List
from pypdf import PdfReader
from docx import Document

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from knowledge_base import KnowledgeBaseService

router = APIRouter()

_kb_service = None

def get_kb_service():
    """获取知识库服务实例（延迟初始化）"""
    global _kb_service
    if _kb_service is None:
        _kb_service = KnowledgeBaseService()
    return _kb_service

class UploadResponse(BaseModel):
    message: str
    file_name: str
    success: bool

class BatchUploadResponse(BaseModel):
    total: int
    success_count: int
    failed_count: int
    results: List[dict]

class DocumentInfo(BaseModel):
    id: str
    source: str
    create_time: str
    content_preview: str

def extract_text_from_file(file: UploadFile, content: bytes) -> str:
    """从文件内容中提取文本"""
    if file.filename.lower().endswith('.txt'):
        return content.decode("utf-8")
    elif file.filename.lower().endswith('.pdf'):
        pdf_reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    elif file.filename.lower().endswith('.docx'):
        doc = Document(io.BytesIO(content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    return ""

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """上传单个文件到知识库"""
    try:
        allowed_extensions = ['.txt', '.pdf', '.docx']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail="只支持.txt, .pdf, .docx文件")

        content = await file.read()
        text = extract_text_from_file(file, content)
        
        result = get_kb_service().upload_by_str(text, file.filename)

        return UploadResponse(
            message=result,
            file_name=file.filename,
            success=True
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/batch", response_model=BatchUploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """批量上传文件到知识库"""
    if not files:
        raise HTTPException(status_code=400, detail="请至少选择一个文件")
    
    allowed_extensions = ['.txt', '.pdf', '.docx']
    results = []
    success_count = 0
    failed_count = 0
    
    for file in files:
        try:
            # 检查文件类型
            if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
                results.append({
                    "file_name": file.filename,
                    "success": False,
                    "message": "不支持的文件格式"
                })
                failed_count += 1
                continue
            
            # 提取文本
            content = await file.read()
            text = extract_text_from_file(file, content)
            
            # 上传到知识库
            result = get_kb_service().upload_by_str(text, file.filename)
            
            results.append({
                "file_name": file.filename,
                "success": True,
                "message": result
            })
            success_count += 1
            
        except Exception as e:
            results.append({
                "file_name": file.filename,
                "success": False,
                "message": str(e)
            })
            failed_count += 1
    
    return BatchUploadResponse(
        total=len(files),
        success_count=success_count,
        failed_count=failed_count,
        results=results
    )

@router.get("/documents", response_model=list[DocumentInfo])
async def list_documents():
    """获取知识库中的所有文档"""
    try:
        docs = get_kb_service().list_documents()
        
        documents = []
        for doc in docs:
            documents.append(DocumentInfo(
                id=doc['source'],
                source=doc['source'],
                create_time=doc['create_time'],
                content_preview=f"包含 {doc['chunk_count']} 个文本块"
            ))
        
        return documents
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """删除指定的文档"""
    try:
        result = get_kb_service().delete_document(document_id)
        return {"message": result, "success": "成功" in result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))