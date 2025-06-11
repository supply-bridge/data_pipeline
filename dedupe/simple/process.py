import dedupe
import pandas as pd
from unidecode import unidecode

# 🔹 加载数据
df = pd.read_csv('mock_data.csv')
df["DUNS Number"] = df["DUNS Number"].fillna("unknown").astype(str)
data = df.to_dict(orient='records')

# 🔹 数据预处理
def pre_process(column):
    if not isinstance(column, str):
        return 'unknown'
    processed = unidecode(column.lower().strip())
    return processed if processed else 'unknown'

for record in data:
    for key, value in record.items():
        record[key] = pre_process(value)

# 将数据转换为dedupe需要的格式
formatted_data = {str(i): record for i, record in enumerate(data)}
print("Total records:", len(formatted_data))

# 🔹 定义去重模型
fields = [
    dedupe.variables.Exact("DUNS Number", has_missing=True),  # 唯一标识字段
    dedupe.variables.String("Company Name"),  # 允许拼写差异匹配
    dedupe.variables.String("Address"),  # 允许地址格式不同但匹配
    dedupe.variables.String("Contact"),  # 联系人模糊匹配
    dedupe.variables.Exact("Phone")  # 电话完全匹配
]

deduper = dedupe.Dedupe(fields)

# 🔹 训练模型
deduper.prepare_training(formatted_data)
with open('training.json', 'w') as f:
    deduper.write_training(f)

# Add training examples
print('Starting active labeling...')
print('Please label at least 5-10 pairs of records as matches (y) and 5-10 pairs as non-matches (n)')
print('You need to provide examples of both matches and non-matches for the model to train properly')
dedupe.console_label(deduper)

deduper.train()  # 训练模型

# 🔹 进行去重和匹配
clustered_dupes = deduper.partition(formatted_data, threshold=0.6)  # 进行匹配，0.6 代表适中严格度
print("\nClustered duplicates:", clustered_dupes)

# 🔹 合并相似记录
def merge_records(clustered_dupes, df):
    merged_records = []
    for cluster in clustered_dupes:
        merged = {}
        for record_id in cluster:
            record = formatted_data[record_id]
            for key, value in record.items():
                merged[key] = merged.get(key, '') or value  # 选取最完整的数据
        merged_records.append(merged)
    return merged_records

final_data = merge_records(clustered_dupes, df)
final_df = pd.DataFrame(final_data)
final_df.to_csv('final_data.csv', index=False)
print("\nFinal deduplicated data saved to final_data.csv")
print(f"Original records: {len(df)}")
print(f"Deduplicated records: {len(final_df)}")
