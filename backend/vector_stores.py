from langchain_chroma import Chroma
import config_data as config
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document


class SimpleEnsembleRetriever:
    """混合检索器（向量检索+BM25）"""
    def __init__(self, retrievers, weights):
        self.retrievers = retrievers
        self.weights = weights

    def invoke(self, query):
        """执行混合检索"""
        all_docs = []
        for retriever, weight in zip(self.retrievers, self.weights):
            docs = retriever.invoke(query)
            for doc in docs:
                if 'ensemble_score' not in doc.metadata:
                    doc.metadata['ensemble_score'] = 0
                doc.metadata['ensemble_score'] += weight
                all_docs.append(doc)
        
        all_docs.sort(key=lambda x: x.metadata.get('ensemble_score', 0), reverse=True)
        return all_docs[:config.ensemble_k]


class VectorStoreService(object):
    def __init__(self, embedding):
        """初始化向量存储服务"""
        self.embedding = embedding
        self.vector_store = Chroma(
            collection_name=config.collection_name,
            embedding_function=self.embedding,
            persist_directory=config.persist_directory,
        )
        
        chroma_data = self.vector_store.get(include=['documents'])
        self.docs = [Document(page_content=doc) for doc in chroma_data['documents']]
        
        if self.docs:
            self.bm25_retriever = BM25Retriever.from_documents(self.docs)
            self.bm25_retriever.k = config.ensemble_k
        else:
            self.bm25_retriever = None

    def get_retriever(self):
        """获取混合检索器（向量检索+BM25）"""
        vector_retriever = self.vector_store.as_retriever(search_kwargs={"k": config.similarity_threshold})
        if self.bm25_retriever:
            ensemble_retriever = SimpleEnsembleRetriever(
                retrievers=[vector_retriever, self.bm25_retriever],
                weights=[config.vector_weight, config.bm25_weight]
            )
            return ensemble_retriever
        else:
            return vector_retriever


if __name__ == "__main__":
    """
    简单的测试代码
    测试 VectorStoreService 的初始化和检索器获取功能
    无论从哪个路径执行本文件，都会先将当前工作目录切换为脚本所在目录。
    """
    import os
    from dotenv import load_dotenv
    from langchain_community.embeddings import DashScopeEmbeddings

    # 将当前工作目录切换为脚本所在目录，保证相对路径（如 ./chroma_db、./md5.text）始终指向项目目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"[info] 已将当前工作目录切换为脚本所在目录: {script_dir}")

    # 加载环境变量
    load_dotenv()
    
    # 获取 API key
    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        print("警告: 未找到 DASHSCOPE_API_KEY 或 API_KEY 环境变量，测试可能失败")
        print("请先在 .env 或系统环境中配置 API key")
    else:
        os.environ["DASHSCOPE_API_KEY"] = api_key
    
    try:
        print("=" * 50)
        print("开始测试 VectorStoreService")
        print("=" * 50)
        
        # 1. 创建 embedding 模型
        print("\n[1] 创建 embedding 模型...")
        embedding = DashScopeEmbeddings(model="text-embedding-v4")
        print("✓ Embedding 模型创建成功")
        
        # 2. 初始化 VectorStoreService
        print("\n[2] 初始化 VectorStoreService...")
        vector_service = VectorStoreService(embedding)
        print("✓ VectorStoreService 初始化成功")
        print(f"  - Collection name: {config.collection_name}")
        print(f"  - Persist directory: {config.persist_directory}")
        
        # 3. 获取检索器
        print("\n[3] 获取检索器...")
        retriever = vector_service.get_retriever()
        print("✓ 检索器获取成功")
        print(f"  - Search k: {config.similarity_threshold}")
        
        # 4. 测试检索功能（如果向量库中有数据）
        print("\n[4] 测试检索功能...")
        try:
            # 尝试检索一个测试查询
            test_query = "测试查询"
            results = retriever.invoke(test_query)
            print(f"✓ 检索成功，返回 {len(results)} 个文档")
            if results:
                print(f"  第一个文档预览: {results[0].page_content[:100]}...")
            else:
                print("  注意: 向量库中暂无数据，这是正常的（如果还没有上传文档）")
        except Exception as e:
            print(f"  注意: 检索测试时出现异常（可能是向量库为空）: {str(e)}")
        
        print("\n" + "=" * 50)
        print("测试完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        