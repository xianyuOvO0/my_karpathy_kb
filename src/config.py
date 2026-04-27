# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

load_dotenv()

# API 配置
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
BASE_URL = "https://api.siliconflow.cn/v1"
MODEL_NAME = "deepseek-ai/DeepSeek-V3"   # 可换成其他长上下文模型

# 目录配置
RAW_DIR = "raw"
WIKI_DIR = "wiki"
OUTPUTS_DIR = "outputs"
SESSIONS_DIR = os.path.join(OUTPUTS_DIR, "sessions")

# 编译参数
COMPILE_TEMPERATURE = 0.3
COMPILE_MAX_TOKENS = 16000

# 问答参数
QUERY_TEMPERATURE = 0.3
QUERY_MAX_TOKENS = 2000

# 支持的文件扩展名
SUPPORTED_EXTS = ('.txt', '.md', '.pdf', '.html', '.docx')