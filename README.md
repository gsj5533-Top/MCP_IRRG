# McpIrrg 智能灌溉知识库MCP Server

本项目基于 Qwen3 大模型、LangChain 框架、Chroma 向量数据库、PostgreSQL，支持文档采集、向量化、意图识别、交互式选项、配置文件扩展、定时采集、智能决策等功能。

## 主要功能
- 用户意图判断与交互式选项
- 文档采集与向量化入库
- PostgreSQL 数据库管理
- LangChain 串联智能体能力

## 依赖安装
```bash
pip install -r requirements.txt
```

## 参考
- Qwen3
- LangChain
- ChromaDB
- PostgreSQL
- Jina Embeddings


pip install pywin32
pip install fastapi uvicorn
# 命令行模式
python main.py
# 服务器模式（需先实现）
uvicorn server:app --host 0.0.0.0 --port 8000
