import dedupe
import pandas as pd
import random

# 🔹 创建模拟供应商数据
data = []

# 定义一些常见的公司名称变体
company_variations = {
    'Ltd': ['Ltd', 'Limited', 'Ltd.', 'LLC', 'Inc', 'Inc.'],
    'Street': ['Street', 'St', 'St.', 'Avenue', 'Ave', 'Ave.'],
    'Company': ['Company', 'Co', 'Co.', 'Corp', 'Corp.', 'Corporation']
}

# 定义一些常见的拼写错误
typos = {
    'a': ['a', 'e', 'o'],
    'e': ['e', 'i', 'a'],
    'i': ['i', 'y', 'e'],
    'o': ['o', 'u', 'a'],
    'u': ['u', 'o', 'a']
}

def add_typos(text):
    """随机添加一些拼写错误"""
    if random.random() < 0.3:  # 30%的概率添加拼写错误
        chars = list(text)
        for i in range(len(chars)):
            if chars[i].lower() in typos and random.random() < 0.3:
                chars[i] = random.choice(typos[chars[i].lower()])
        return ''.join(chars)
    return text

def get_company_variation(name):
    """生成公司名称的变体"""
    if random.random() < 0.7:  # 70%的概率使用变体
        for key, variations in company_variations.items():
            if key in name:
                name = name.replace(key, random.choice(variations))
    return name

# 首先创建一些基础记录
base_records = []
for i in range(1, 51):  # 创建50条基础记录
    # 随机决定是否包含DUNS号
    duns = f"{random.randint(100000, 999999)}" if random.random() < 0.8 else None
    
    # 生成基础公司名
    base_company = f"Company {i}"
    # 添加变体和拼写错误
    company_name = get_company_variation(base_company)
    company_name = add_typos(company_name)
    
    # 生成地址，随机决定是否包含完整信息
    if random.random() < 0.7:  # 70%的概率包含完整地址
        address = f"{i} Main {random.choice(['Street', 'St', 'St.', 'Avenue', 'Ave'])}"
        if random.random() < 0.5:
            address += f", City {i}"
        if random.random() < 0.3:
            address += f", {random.choice(['NY', 'CA', 'TX', 'FL'])} {random.randint(10000, 99999)}"
    else:
        address = None
    
    # 生成联系人，随机决定是否包含
    if random.random() < 0.8:  # 80%的概率包含联系人
        contact = f"Contact {i}"
        if random.random() < 0.5:
            contact += f" {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}"
        contact = add_typos(contact)
    else:
        contact = None
    
    # 生成电话，随机决定是否包含
    if random.random() < 0.9:  # 90%的概率包含电话
        phone = f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    else:
        phone = None
    
    base_records.append({
        'id': i,
        'DUNS Number': duns,
        'Company Name': company_name,
        'Address': address,
        'Contact': contact,
        'Phone': phone
    })

# 添加一些重复记录
for i in range(51, 101):
    # 随机选择一个基础记录
    base = random.choice(base_records)
    # 随机决定是复制DUNS还是公司名
    if random.random() < 0.5:
        # 复制DUNS，但其他信息不同
        duns = base['DUNS Number']
        company_name = get_company_variation(f"Company {i}")
        company_name = add_typos(company_name)
    else:
        # 复制公司名，但其他信息不同
        duns = f"{random.randint(100000, 999999)}" if random.random() < 0.8 else None
        company_name = get_company_variation(base['Company Name'])
        company_name = add_typos(company_name)
    
    # 生成其他随机信息，保持一些字段缺失
    if random.random() < 0.7:
        address = f"{i} Main {random.choice(['Street', 'St', 'St.', 'Avenue', 'Ave'])}"
        if random.random() < 0.5:
            address += f", City {i}"
        if random.random() < 0.3:
            address += f", {random.choice(['NY', 'CA', 'TX', 'FL'])} {random.randint(10000, 99999)}"
    else:
        address = None
    
    if random.random() < 0.8:
        contact = f"Contact {i}"
        if random.random() < 0.5:
            contact += f" {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}"
        contact = add_typos(contact)
    else:
        contact = None
    
    if random.random() < 0.9:
        phone = f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    else:
        phone = None
    
    data.append({
        'id': i,
        'DUNS Number': duns,
        'Company Name': company_name,
        'Address': address,
        'Contact': contact,
        'Phone': phone
    })

# 将基础记录也添加到数据中
data.extend(base_records)

# 随机打乱数据顺序
random.shuffle(data)

# 将数据保存到文件
df = pd.DataFrame(data)
df.to_csv('mock_data.csv', index=False)
print("Mock data saved to mock_data.csv")
print(f"Total records: {len(data)}")
print("\nSample of generated data:")
print(df.head().to_string())
print("\nMissing values in each column:")
print(df.isnull().sum())
