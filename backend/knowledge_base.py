"""
知识库服务类
管理文件上传、MD5校验和向量数据库存储
"""
import hashlib
import os
from datetime import datetime

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config_data as config


class KnowledgeBaseService(object):
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # 兼容两种环境变量命名方式
        api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("API_KEY")
        if not api_key:
            raise ValueError(
                "未找到 DASHSCOPE_API_KEY 或 API_KEY 环境变量，请先在 .env 或系统环境中配置后再运行。"
            )
        
        # LangChain 的 DashScopeEmbeddings 会自动从环境变量中读取 key
        os.environ["DASHSCOPE_API_KEY"] = api_key
        
        os.makedirs(config.persist_directory, exist_ok=True)
        
        self.chroma = Chroma(
            collection_name=config.collection_name,
            embedding_function=DashScopeEmbeddings(model="text-embedding-v4"),
            persist_directory=config.persist_directory,
        )
        
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            length_function=len,
        )

    def check_md5(self, md5_str):
        """检查MD5是否已存在"""
        if not os.path.exists(config.md5_path):
            return False
        
        with open(config.md5_path, 'r', encoding='utf-8') as f:
            existing_md5s = f.read().splitlines()
        
        return md5_str in existing_md5s

    def save_md5(self, md5_str):
        """保存MD5到文件"""
        os.makedirs(os.path.dirname(config.md5_path) if os.path.dirname(config.md5_path) else '.', exist_ok=True)
        
        with open(config.md5_path, 'a', encoding='utf-8') as f:
            f.write(md5_str + '\n')

    def get_string_md5(self, str_data):
        """计算字符串的MD5值"""
        md5_hash = hashlib.md5()
        md5_hash.update(str_data.encode('utf-8'))
        return md5_hash.hexdigest()

    def upload_by_str(self, data: str, filename):
        """将文本内容向量化并存入向量数据库"""
        md5_hex = self.get_string_md5(data)
        if self.check_md5(md5_hex):
            return "[跳过]内容已经存在知识库中"
        
        knowledge_chunks: list[str] = self.spliter.split_text(data)
        
        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "系统",
        }
        
        self.chroma.add_texts(
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks],
        )
        
        self.save_md5(md5_hex)
        return "[成功]内容已经成功载入向量库"

    def list_documents(self):
        """列出所有文档信息"""
        data = self.chroma.get(include=['metadatas'])
        documents = {}
        
        for metadata in data['metadatas']:
            source = metadata.get('source', '未知')
            if source not in documents:
                documents[source] = {
                    'source': source,
                    'create_time': metadata.get('create_time', '未知'),
                    'chunk_count': 0
                }
            documents[source]['chunk_count'] += 1
        
        return list(documents.values())

    def delete_document(self, source_filename):
        """根据文件名删除文档的所有块"""
        try:
            # 删除匹配的文档
            self.chroma.delete(where={"source": source_filename})
            return f"[成功]已删除文档: {source_filename}"
        except Exception as e:
            return f"[失败]删除文档失败: {str(e)}"
