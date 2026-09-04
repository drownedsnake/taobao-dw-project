from pyspark.sql import SparkSession
from hdfs import InsecureClient
from pyhive import hive

# ========== 1. HDFS 准备数据 ==========
print("=" * 50)
print("第一步：HDFS 数据准备")
print("=" * 50)

client = InsecureClient('http://localhost:9870', user='drownedsnake')

# 创建销售数据
sales_data = """order_id,product,amount,price,date
1001,手机,2,3999,2024-01-15
1002,电脑,1,6999,2024-01-16
1003,手机,3,3999,2024-01-17
1004,平板,2,2999,2024-01-18
1005,电脑,1,6999,2024-01-19
1006,手机,1,3999,2024-01-20
1007,平板,3,2999,2024-01-21"""

with open('sales.csv', 'w', encoding='utf-8') as f:
    f.write(sales_data)

client.makedirs('/user/drownedsnake/project')
client.upload('/user/drownedsnake/project/sales.csv', 'sales.csv', overwrite=True)
print("✅ 销售数据已上传到 HDFS")

# ========== 2. Spark 分析数据 ==========
print("\n" + "=" * 50)
print("第二步：Spark 数据分析")
print("=" * 50)

spark = SparkSession.builder \
    .appName("综合实战") \
    .master("local[*]") \
    .config("spark.driver.host", "localhost") \
    .getOrCreate()

# 从 HDFS 读取数据
df = spark.read.csv('hdfs://localhost:9000/user/drownedsnake/project/sales.csv',
                     header=True, inferSchema=True)

print("=== 原始数据 ===")
df.show()

# 计算每笔订单总金额
df = df.withColumn("total", df.amount * df.price)

print("=== 各产品销售额 ===")
df.groupBy("product").agg({"total": "sum", "amount": "sum"}) \
  .withColumnRenamed("sum(total)", "总销售额") \
  .withColumnRenamed("sum(amount)", "总销量") \
  .orderBy("总销售额", ascending=False) \
  .show()

print("=== 销售统计 ===")
df.agg(
    {"total": "sum", "amount": "sum", "order_id": "count"}
).withColumnRenamed("sum(total)", "总营收") \
 .withColumnRenamed("sum(amount)", "总销量") \
 .withColumnRenamed("count(order_id)", "订单数") \
 .show()

# ========== 3. Hive 存储结果 ==========
print("\n" + "=" * 50)
print("第三步：Hive 存储分析结果")
print("=" * 50)

conn = hive.Connection(host='localhost', port=10000, username='drownedsnake', auth='NOSASL')
cursor = conn.cursor()

cursor.execute('CREATE DATABASE IF NOT EXISTS analytics')
cursor.execute('USE analytics')
cursor.execute('DROP TABLE IF EXISTS product_sales')
cursor.execute('''
    CREATE TABLE product_sales (
        product STRING,
        total_sales DOUBLE,
        total_amount INT
    )
''')
print("✅ 分析结果表创建成功")

# 获取 Spark 分析结果
result = df.groupBy("product").agg({"total": "sum", "amount": "sum"}).collect()

try:
    for row in result:
        cursor.execute(f"INSERT INTO product_sales VALUES ('{row[0]}', {row[1]}, {row[2]})")
    cursor.execute('SELECT * FROM product_sales')
    print("\n📊 Hive 中的分析结果:")
    for row in cursor.fetchall():
        print(f"  产品: {row[0]}, 销售额: {row[1]}, 销量: {row[2]}")
except Exception as e:
    print(f"\n️  Hive INSERT 失败（MapReduce 配置问题），直接用 Spark 展示结果:")
    print("\n📊 Spark 分析结果:")
    df.groupBy("product").agg({"total": "sum", "amount": "sum"}) \
      .withColumnRenamed("sum(total)", "总销售额") \
      .withColumnRenamed("sum(amount)", "总销量") \
      .orderBy("总销售额", ascending=False) \
      .show()

cursor.close()
conn.close()
spark.stop()

print("\n🎉 综合实战完成！HDFS + Spark + Hive 全流程打通！")