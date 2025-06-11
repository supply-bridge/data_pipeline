import os
from dotenv import load_dotenv
load_dotenv()  # 默认从当前目录的 .env 加载

EMBEDDING_MODEL = "text-embedding-3-small"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "5432")),
}

# 这个值根据实际效果调节，越小要求越严格
MIN_CONFIDENCE_SCORE = float(os.getenv("MIN_CONFIDENCE_SCORE", 0.3))
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
