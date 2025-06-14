from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import psycopg2
import json
from config import DB_CONFIG,TAVILY_API_KEY
# from tavily import TavilyClient

# tvl_client = TavilyClient(api_key=TAVILY_API_KEY)
#
from urllib.parse import urlparse
import requests
from pydantic import RootModel, ValidationError
from typing import List

class CategoryList(RootModel[list[str]]):
  pass

def is_valid_url_with_fallback(url: str, timeout=3) -> str | None:
    """
    尝试 https -> http，返回有效的网址或 None
    """
    for scheme in ("https", "http"):
        try:
            test_url = normalize_url(url, scheme)
            response = requests.head(test_url, allow_redirects=True, timeout=timeout)
            if response.status_code < 400:
                return test_url
            # fallback to GET if HEAD fails
            response = requests.get(test_url, allow_redirects=True, timeout=timeout)
            if response.status_code < 400:
                return test_url
        except requests.RequestException:
            continue
    return None

def normalize_url(url: str, scheme: str = "https") -> str:
    if not url:
        return ""
    url = url.strip()
    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"{scheme}://{url}"
    return url

# --- 配置数据库连接 ---
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# --- 读取供应商网站列表 ---
cursor.execute("select distinct on (website) id, website from sb_supplier_cluster_test where website is not null and website!='' limit 10")
suppliers = cursor.fetchall()

# --- 初始化 LLM ---
llm = ChatOpenAI(temperature=0)

# --- 定义 Prompt 模板 ---
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的供应链分析师。"),
    ("human", """请访问以下网站内容，并告诉我这家公司提供的汽车零部件分类。\
格式必须是 JSON array，例如：["发动机", "车灯"]。\n\n\
⚠️ 请注意：**不要使用 Markdown 格式**，不要添加 ```json 代码块包装，只返回原始 JSON 数组。\n\n{page_content}""")
])

# --- 遍历每个供应商 ---
for supplier_id, website in suppliers:
  valid_url = is_valid_url_with_fallback(website)
  if valid_url:
      # Step 2: 用 WebBaseLoader 加载
      loader = WebBaseLoader(valid_url)
      docs = loader.load()
      print(f"Loaded {len(docs)} documents from {valid_url}")
  else:
      print(f"[✗] Website unreachable: {website}")
      continue

  docs = loader.load()
  page_content = docs[0].page_content[:3000]  # 限制输入长度

  chain = prompt | llm
  result = chain.invoke({"page_content": page_content})
  # result 很可能直接是字符串，无需 .content
  response_text = result if isinstance(result, str) else getattr(result, "content", "")
  print("LLM 返回内容（前500字符）：", response_text[:500])

  try:
      data = CategoryList.model_validate_json(response_text.strip())
      categories = data.root
  except json.JSONDecodeError as e:
      print("[✗] Pydantic 验证失败，内容不符合格式")
      print(e)
      categories = []

  if categories:
      pg_array = "{" + ",".join(f'"{c}"' for c in categories) + "}"

      cursor.execute(
          "UPDATE sb_supplier_cluster_test SET tag_cluster = %s WHERE id = %s",
          (pg_array, supplier_id)
      )
      print(f"[OK] id={supplier_id}, 分类={categories}")
  else:
      print(f"[Skip] id={supplier_id}, 无有效分类：{response_text}")

conn.commit()
cursor.close()
conn.close()
