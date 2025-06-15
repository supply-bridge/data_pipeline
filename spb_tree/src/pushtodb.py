import csv
import json
import argparse
import psycopg2
import os
from tqdm import tqdm
from psycopg2.extras import execute_batch


# 解析命令行参数
parser = argparse.ArgumentParser(description="Push JSON data to database")
parser.add_argument("input_file", help="Input JSON file")
parser.add_argument("--csv", help="Optional: Output CSV filename")
args = parser.parse_args()

# 数据库配置
DB_NAME = "supplybridge"
DB_USER = "sbadmintest"
DB_PASSWORD = "87pm<z-YVO?jFYtHU}!=g]Nm"
DB_HOST = "supplybridge-pg-test-fc90ks.postgres.database.azure.com"
DB_PORT = 5432

# 连接数据库
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
)
cursor = conn.cursor()

conn.autocommit = False
# 获取当前数据库中的最大 ID
cursor.execute("SELECT nextval('sb_offering_id_seq')")
next_available_id = cursor.fetchone()[0]

# 读取 JSON 文件
with open(args.input_file, "r", encoding="utf-8") as file:
    data = json.load(file)

cursor.execute("TRUNCATE offering_load RESTART IDENTITY")

# 创建索引以优化查询
node_index = {node["uid"]: node for node in data["nodes"]}

# 扁平化数据
flat_list = []
id_mapping = {}  # 旧 UID 映射到新 ID
visited_nodes = set()  # 防止重复处理相同节点
all_fields = {"id", "pid"}  # 记录所有字段


# **分配唯一 id，仅处理带字母的 uid**
def assign_ids(node):
    global next_available_id
    uid = node["uid"]

    # **如果 uid 是纯数字，直接使用**
    if uid.isdigit():
        id_mapping[uid] = int(uid)
    else:
        # **否则分配新的 ID**
        id_mapping[uid] = next_available_id
        next_available_id += 1

    # 递归处理子节点
    for child_uid in node["children"]:
        child_node = node_index.get(child_uid)
        if child_node:
            assign_ids(child_node)


# 处理 `topnodes`（根节点）
for top_uid in data["properties"]["topnodes"]:
    top_node = node_index.get(top_uid)
    if top_node:
        assign_ids(top_node)


# **扁平化数据**
def flatten_nodes(node, parent_uid=None):
    if node["uid"] in visited_nodes:
        return
    visited_nodes.add(node["uid"])

    node_id = id_mapping[node["uid"]]
    parent_id_int = None if parent_uid is None else id_mapping.get(parent_uid)

    if parent_id_int is not None and not isinstance(parent_id_int, int):
        print(
            f"Warning: pid {parent_id_int} is not an integer, setting to NULL"
        )
        parent_id_int = None

    record = {"id": node_id, "pid": parent_id_int}

    for key, value in node["data"].items():
        record[key] = value
        all_fields.add(key)

    flat_list.append(record)

    for child_uid in node["children"]:
        child_node = node_index.get(child_uid)
        if child_node:
            flatten_nodes(child_node, node["uid"])


for top_uid in data["properties"]["topnodes"]:
    top_node = node_index.get(top_uid)
    if top_node:
        flatten_nodes(top_node)

# **计算所有字段**
all_fields = sorted(all_fields)
columns = ", ".join(all_fields)
placeholders = ", ".join(["%s"] * len(all_fields))
sql = f"INSERT INTO offering_load ({columns}) VALUES ({placeholders})"

# **确保数据顺序正确**
data_to_insert = [
    [record.get(col, None) for col in all_fields] for record in flat_list
]

# **写入 CSV**
if args.csv:
    csv_file = args.csv
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=all_fields)
        writer.writeheader()
        writer.writerows(flat_list)
    print(f"DEBUG: CSV file saved -> {csv_file}")

# **批量插入数据库**
batch_size = 500
with tqdm(total=len(data_to_insert), desc="Bulk Insert into DB") as pbar:
    execute_batch(cursor, sql, data_to_insert, page_size=batch_size)
    pbar.update(len(data_to_insert))

conn.commit()

# **执行 UPSERT**
upsert_sql = """
INSERT INTO sb_offering (id, pid, name, name_de, description, original_name, source, alternative_name)
SELECT id, pid, name, name_de, description, original_name, source, alternative_name
FROM offering_fields
ON CONFLICT (id) DO UPDATE
SET pid = EXCLUDED.pid,
    name = EXCLUDED.name,
    name_de = EXCLUDED.name_de,
    description = EXCLUDED.description,
    original_name = EXCLUDED.original_name,
    source = EXCLUDED.source,
    alternative_name = EXCLUDED.alternative_name;
"""
cursor.execute(upsert_sql)
conn.commit()

# # **执行 DELETE**
# delete_sql = """
# DELETE FROM sb_offering
# WHERE id NOT IN (SELECT id FROM offering_load);
# """
# cursor.execute(delete_sql)
# conn.commit()

# **关闭数据库连接**
cursor.close()
conn.close()

print("Data has been synced into DB successfully!")
