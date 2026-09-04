from pyhive import hive
from hdfs import InsecureClient

# ========== 1. 上传原始数据到 HDFS ==========
client = InsecureClient('http://localhost:9870', user='drownedsnake')

# 模拟原始业务数据（原封不动，不做任何处理）
raw_data = """order_id,product,amount,price,date,region
1001,手机,2,3999,2024-01-15,华北
1002,电脑,1,6999,2024-01-16,华东
1003,手机,3,3999,2024-01-17,华南
1004,平板,2,2999,2024-01-18,华北
1005,电脑,1,6999,2024-01-19,华东
1006,手机,1,3999,2024-01-20,华南
1007,平板,3,2999,2024-01-21,华北"""

with open('raw_sales.csv', 'w', encoding='utf-8') as f:
    f.write(raw_data)

# 上传到 HDFS 的 ODS 目录
client.makedirs('/user/drownedsnake/ods/sales')
client.upload('/user/drownedsnake/ods/sales/raw_sales.csv', 'raw_sales.csv', overwrite=True)
print("✅ 原始数据已上传到 HDFS ODS 目录")

# ========== 2. 创建 ODS 层数据库和表 ==========
conn = hive.Connection(host='localhost', port=10000, username='drownedsnake', auth='NOSASL')
cursor = conn.cursor()

# 创建 ODS 数据库
cursor.execute('CREATE DATABASE IF NOT EXISTS ods')
cursor.execute('USE ods')

# 删除旧表
cursor.execute('DROP TABLE IF EXISTS ods_sales_raw')

# 创建 ODS 表（字段和原始数据完全一致，不做任何加工）
cursor.execute('''
    CREATE TABLE ods_sales_raw (
        order_id INT,
        product STRING,
        amount INT,
        price DOUBLE,
        `date` STRING,
        region STRING
    )
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    STORED AS TEXTFILE
''')
print("✅ ODS 表创建成功")

# ========== 3. LOAD DATA 加载数据（不走 MapReduce！）==========
# 从 HDFS 加载（移动文件到 Hive 仓库目录）
cursor.execute("LOAD DATA INPATH '/user/drownedsnake/ods/sales/raw_sales.csv' INTO TABLE ods_sales_raw")
print("✅ LOAD DATA 成功（不走 MapReduce）")

# 验证数据
cursor.execute('SELECT * FROM ods_sales_raw')
print("\n📊 ODS 层原始数据:")
for row in cursor.fetchall():
    print(f"  {row}")

# 查看表结构
cursor.execute('DESC ods_sales_raw')
print("\n📋 表结构:")
for row in cursor.fetchall():
    print(f"  {row}")

cursor.close()
conn.close()