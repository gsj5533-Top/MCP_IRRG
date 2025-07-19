from agents.irrigation_agent import IrrigationAgent
from langchain.agents import initialize_agent, AgentType
from langchain.llms import Ollama
from db.pg_manager import PgManager
from db.chroma_manager import ChromaManager
from agents.agent_manager import AgentManager
from utils.ollama_wrapper import OllamaWrapper
import yaml
from langchain_ollama import OllamaEmbeddings

def run_interactive(agent):
    """交互式决策流程（从IrrigationAgent迁移）"""
    print("欢迎使用智能灌溉决策助手！")
    while True:
        user_input = input("请描述您的需求（输入'退出'结束）：")
        if user_input.lower() == '退出':
            break
        try:
            response = agent.invoke({"input": user_input})
            print(f"助手: {response}\n")
        except Exception as e:
            print(f"处理请求时出错: {str(e)}\n")

def main():
    # 加载配置
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 初始化数据库
    pg_db = PgManager(config['pgsql'])  # 使用pgsql配置项
    # 初始化Ollama嵌入模型
    embeddings = OllamaEmbeddings(
        base_url=config['ollama_api_url'],
        model=config['vector_db']['embedding_model']  # 修复：使用向量数据库配置的嵌入模型
    )
    # 传入embeddings参数
    chroma_manager = ChromaManager(config['vector_db'], embeddings)
    chroma_db = chroma_manager.vectorstore  # 直接访问vectorstore属性

    # 创建Ollama包装器（统一管理）
    ollama_wrapper = OllamaWrapper(
        api_url=config['ollama_api_url'],
        model=config['ollama_model'],
        embedding_model=config['vector_db']['embedding_model']
    )

    # 初始化Agent管理器并注册工具
    agent_manager = AgentManager(config, pg_db, chroma_db, ollama_wrapper)
    tools = agent_manager.get_all_tools()

    # 初始化大模型
    llm = Ollama(
        base_url=config['ollama_api_url'],
        model=config['ollama_model'],
        temperature=0
    )

    # 创建工具调用代理
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    # 启动交互循环
    run_interactive(agent)

if __name__ == "__main__":
    main()