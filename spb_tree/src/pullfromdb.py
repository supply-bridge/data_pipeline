import psycopg2
import json
import argparse
from dotenv import load_dotenv
import os
from tqdm import tqdm  # 新增导入


# 解析命令行参数
parser = argparse.ArgumentParser(description="Get offering tree")
parser.add_argument("output_file", help="output filename，default: offering_tree.trln", default="offering_tree.trln")
# parser.add_argument("--root_node_id", type=int, default=None, help="optional：root_node_id，default: get all nodes")
args = parser.parse_args()

# 加载对应环境变量
# env_file = f".env.{args.env}"
DB_NAME="supplybridge"
DB_USER="sbadmintest"
DB_PASSWORD="87pm<z-YVO?jFYtHU}!=g]Nm"
DB_HOST="supplybridge-pg-test-fc90ks.postgres.database.azure.com"
DB_PORT=5432

# 连接到数据库
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

print("Querying database...")

# 调用 PostgreSQL 函数 `get_offering_tree(root_node_id)`
with tqdm(total=3, desc="progress") as pbar:
  cursor.execute("SELECT get_offering_tree(%s);", (None,))
  pbar.update(1)

  result = cursor.fetchone()[0]  # 获取 JSONB 结果
  pbar.update(1)
  # 关闭数据库连接
  cursor.close()
  conn.close()

  # 处理输出文件名，确保 `.trln` 后缀
  if not args.output_file.endswith(".trln"):
      args.output_file+= ".trln"
  pbar.update(1)

# **写入 JSON 文件**
with open(args.output_file, "w", encoding="utf-8") as file:
    json.dump(result, file, ensure_ascii=False, indent=4)

print(f"Data has been saved in {args.output_file}")
