from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yaml
from db.pg_manager import PgManager
from db.chroma_manager import ChromaManager
from agents.agent_manager import AgentManager
from utils.ollama_wrapper import OllamaWrapper
from langchain_ollama import OllamaEmbeddings

app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class IrrigationRequest(BaseModel):
    city: str
    crop: str
    time_range: int = 7

# 全局变量
agent_manager = None

@app.on_event("startup")
async def startup_event():
    """服务启动时初始化组件"""
    global agent_manager

    # 加载配置
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 初始化数据库
    pg_db = PgManager(config['pgsql'])
    
    # 初始化Ollama嵌入模型
    embeddings = OllamaEmbeddings(
        base_url=config['ollama_api_url'],
        model=config['ollama_model']
    )
    
    # 初始化向量数据库
    chroma_manager = ChromaManager(config['vector_db'], embeddings)
    chroma_db = chroma_manager.vectorstore

    # 创建Ollama包装器
    ollama_wrapper = OllamaWrapper(
        api_url=config['ollama_api_url'],
        model=config['ollama_model'],
        embedding_model=config['vector_db']['embedding_model']
    )

    # 初始化Agent管理器
    agent_manager = AgentManager(config, pg_db, chroma_db, ollama_wrapper)

@app.post("/api/irrigation/suggest")
async def get_irrigation_suggestion(request: IrrigationRequest):
    """获取灌溉建议"""
    global agent_manager
    if not agent_manager:
        raise HTTPException(status_code=500, detail="系统未正确初始化")

    try:
        # 获取灌溉建议
        irrigation_agent = agent_manager.agents['irrigation']
        suggestion = irrigation_agent.get_suggestion(
            request.city,
            request.crop,
            request.time_range
        )
        return suggestion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
