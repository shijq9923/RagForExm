from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from file_history_store import get_history
import json


def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt


def debug_runnable(name: str, pretty: bool = False):
    def _convert_to_serializable(obj):
        """将对象转换为可 JSON 序列化的格式，递归处理嵌套结构"""
        # 处理 LangChain 消息对象（HumanMessage, AIMessage, SystemMessage 等）
        if hasattr(obj, 'content') and hasattr(obj, '__class__'):
            class_name = obj.__class__.__name__
            if 'Message' in class_name:
                result = {
                    "type": class_name,
                    "content": obj.content
                }
                # 添加其他可能的属性
                if hasattr(obj, 'additional_kwargs') and obj.additional_kwargs:
                    result["additional_kwargs"] = _convert_to_serializable(obj.additional_kwargs)
                if hasattr(obj, 'response_metadata') and obj.response_metadata:
                    result["response_metadata"] = _convert_to_serializable(obj.response_metadata)
                return result
        
        # 处理 Document 对象
        if isinstance(obj, Document):
            return {
                "page_content": obj.page_content,
                "metadata": obj.metadata
            }
        
        # 处理列表
        if isinstance(obj, list):
            return [_convert_to_serializable(item) for item in obj]
        
        # 处理字典
        if isinstance(obj, dict):
            return {key: _convert_to_serializable(value) for key, value in obj.items()}
        
        # 其他类型，尝试直接返回（如果可序列化）
        try:
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            # 如果无法序列化，返回字符串表示
            return str(obj)
    
    def _inner(x):
        print(f"\n[DEBUG][{name}]")
        
        if pretty:
            # 处理 Document 对象（单个）
            if isinstance(x, Document):
                doc_dict = {
                    "page_content": x.page_content,
                    "metadata": x.metadata
                }
                print(json.dumps(doc_dict, indent=2, ensure_ascii=False))
            # 处理 Document 列表
            elif isinstance(x, list) and len(x) > 0 and isinstance(x[0], Document):
                docs_list = [
                    {
                        "page_content": doc.page_content,
                        "metadata": doc.metadata
                    }
                    for doc in x
                ]
                print(json.dumps(docs_list, indent=2, ensure_ascii=False))
            # 处理普通的 dict 或 list（可能包含消息对象）
            elif isinstance(x, (dict, list)):
                try:
                    serializable_x = _convert_to_serializable(x)
                    print(json.dumps(serializable_x, indent=2, ensure_ascii=False))
                except Exception as e:
                    # 如果序列化失败，回退到直接打印
                    print(f"序列化失败，使用直接打印: {e}")
                    print(x)
            else:
                print(x)
        else:
            print(x)
        
        print(f"[DEBUG][{name}] 结束\n")
        return x

    return RunnableLambda(_inner)


def extract_input_field(x):
    """从输入字典中提取用户查询字符串"""
    if isinstance(x, dict) and "input" in x:
        return x["input"]
    return x


class RagService(object):
    def __init__(self, storage_path: str = None):
        """
        初始化RAG服务
        
        参数:
            storage_path: 会话历史记录存储路径，默认使用config.chat_history_path
        """
        if storage_path is None:
            storage_path = config.chat_history_path
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embedding_model_name)
        )
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "以我提供的已知参考资料为主，简洁和专业的回答用户问题。参考资料:{context}。"),
                ("system", "并且我提供用户的对话历史记录,如下:"),
                MessagesPlaceholder("history"),
                ("user", "请回答用户提问:{input}")
            ]
        )
        self.chat_model = ChatTongyi(model=config.chat_model_name)
        self.storage_path = storage_path

    def _get_chain(self):
        """
        获取RAG执行链（不带历史记录）
        
        输入：用户问题字符串
        输出：LLM回答字符串
        流程：用户问题 -> 向量检索 -> 格式化上下文 -> Prompt模板 -> LLM -> 字符串输出
        """
        retriever = self.vector_service.get_retriever()

        def format_document(docs: list[Document]):
            """格式化检索到的文档为上下文字符串"""
            if not docs:
                return "无相关参考资料"
            formatted_str = ""
            for doc in docs:
                formatted_str += f"文档片段:{doc.page_content}\n文档元数据:{doc.metadata}\n\n"
            return formatted_str

        def extract_history(x):
            """从输入字典中提取历史消息"""
            if isinstance(x, dict) and "history" in x:
                return x["history"]
            return []
        
        inputs_mapping = {
            "input": RunnableLambda(extract_input_field),
            "context": RunnableLambda(extract_input_field) | retriever | format_document,
            "history": RunnableLambda(extract_history),
        }

        rag_chain = (
            inputs_mapping
            | self.prompt_template
            | self.chat_model
            | StrOutputParser()
        )
        return rag_chain

    def get_conversation_chain(self):
        """获取带历史记录的对话链"""
        base_chain = self._get_chain()
        
        def get_history_func(session_id: str):
            return get_history(session_id, self.storage_path)
        
        conversation_chain = RunnableWithMessageHistory(
            base_chain,
            get_history_func,
            input_messages_key="input",
            history_messages_key="history",
        )
        return conversation_chain


if __name__ == "__main__":
    """
    简单的测试代码
    测试 RagService 的初始化、链获取和查询功能（带历史记录）
    无论从哪个路径执行本文件，都会先将当前工作目录切换为脚本所在目录。
    """
    import os
    from dotenv import load_dotenv

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
        print("开始测试 RagService（带历史记录功能）")
        print("=" * 50)
        
        # 1. 初始化 RagService
        print("\n[1] 初始化 RagService...")
        rag_service = RagService()
        print("✓ RagService 初始化成功")
        print(f"  - Embedding model: {config.embedding_model_name}")
        print(f"  - Chat model: {config.chat_model_name}")
        print(f"  - 会话历史存储路径: {rag_service.storage_path}")
        
        # 2. 获取带历史记录的对话链
        print("\n[2] 获取带历史记录的对话链...")
        conversation_chain = rag_service.get_conversation_chain()
        print("✓ 对话链获取成功")
        
        # 3. 配置会话ID
        session_id = "test_user_001"
        session_config = {"configurable": {"session_id": session_id}}
        print(f"\n[3] 配置会话ID: {session_id}")
        print(f"  session_config = {session_config}")
        
        # 4. 测试多轮对话功能
        print("\n[4] 测试多轮对话功能...")
        print("=" * 50)
        
        # 第一轮对话
        print("\n【第一轮对话】")
        test_query_1 = "什么是机器学习？请简要说明其基本概念。"
        print(f"  用户提问: {test_query_1}")
        print("-" * 50)
        try:
            result_1 = conversation_chain.invoke(
                {"input": test_query_1},
                config=session_config
            )
            print(f"✓ 第一轮对话成功")
            print(f"  回答: {result_1}")
        except Exception as e:
            print(f"  注意: 查询时出现异常（可能是向量库为空或 API 配置问题）: {str(e)}")
            print("  这是正常的（如果还没有上传文档或 API key 未配置）")
        print("-" * 50)
        
        # 第二轮对话（测试历史记忆）
        print("\n【第二轮对话】")
        test_query_2 = "我刚才问的身高和体重是多少？"
        print(f"  用户提问: {test_query_2}")
        print("-" * 50)
        try:
            result_2 = conversation_chain.invoke(
                {"input": test_query_2},
                config=session_config
            )
            print(f"✓ 第二轮对话成功")
            print(f"  回答: {result_2}")
            print("  说明: 模型应该能够记住第一轮对话中的身高和体重信息")
        except Exception as e:
            print(f"  注意: 查询时出现异常: {str(e)}")
        print("-" * 50)
        
        # 第三轮对话（继续测试历史记忆）
        print("\n【第三轮对话】")
        test_query_3 = "机器学习的常见算法有哪些？"
        print(f"  用户提问: {test_query_3}")
        print("-" * 50)
        try:
            result_3 = conversation_chain.invoke(
                {"input": test_query_3},
                config=session_config
            )
            print(f"✓ 第三轮对话成功")
            print(f"  回答: {result_3}")
            print("  说明: 模型应该能够结合之前的身高体重信息给出建议")
        except Exception as e:
            print(f"  注意: 查询时出现异常: {str(e)}")
        print("-" * 50)
        
        print("\n" + "=" * 50)
        print("测试完成！")
        print("=" * 50)
        print("\n说明:")
        print("- 会话历史记录已保存到文件中，程序重启后仍然保留")
        print(f"- 会话文件路径: {os.path.join(rag_service.storage_path, session_id)}")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
