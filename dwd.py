import os
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYSPARK_PYTHON"] = r"C:\Users\drownedsnake\AppData\Local\Programs\Python\Python312\python.exe"
os.environ["PYSPARK_DRIVER_PYTHON"] = r"C:\Users\drownedsnake\AppData\Local\Programs\Python\Python312\python.exe"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, trim, upper, lower, regexp_replace, to_date, lit, round as spark_round

spark = SparkSession.builder \
    .appName("DWD数据清洗") \
    .master("local[*]") \
    .config("spark.driver.host", "localhost") \
    .config("spark.pyspark.python", r"C:\Users\drownedsnake\AppData\Local\Programs\Python\Python312\python.exe") \
    .config("spark.pyspark.driver.python", r"C:\Users\drownedsnake\AppData\Local\Programs\Python\Python312\python.exe") \
    .getOrCreate()

# ========== 模拟 ODS 层原始数据（脏数据） ==========
raw_data = [
    (1001, " 手机 ", "2", 3999.0, "2024-01-15", "华北", "张三"),
    (1002, "电脑", "1", 6999.0, "2024/01/16", "华东", "李四"),
    (1003, "手机", "3", 3999.0, "2024-01-17", "华南 ", "王五"),
    (1004, "平板", "2", 2999.0, "2024-01-18", "华北", "赵六"),
    (1005, "电脑", "1", 6999.0, "2024-01-19", "华东", "孙七"),
    (1006, "手机", "1", 3999.0, "2024-01-20", "华南", "周八"),
    (1007, "平板", "3", 2999.0, "2024-01-21", "华北", "吴九"),
    (1001, "手机", "2", 3999.0, "2024-01-15", "华北", "张三"),  # 重复数据
    (1008, "手机", "-1", 3999.0, "2024-01-22", "华东", "郑十"),  # 负数异常
    (1009, "电脑", "0", 6999.0, "2024-01-23", "华南", "冯十一"),  # 数量为0
    (1010, "未知商品", "5", 0.0, "2024-01-24", "华北", "陈十二"),  # 价格为0
]

ods_df = spark.createDataFrame(raw_data, [
    "order_id", "product", "amount", "price", "order_date", "region", "customer_name"
])

print("=" * 60)
print("📋 ODS 层原始数据（脏数据）")
print("=" * 60)
ods_df.show(truncate=False)

# ========== DWD 层数据清洗 ==========
print("=" * 60)
print("🔧 开始 DWD 层数据清洗")
print("=" * 60)

dwd_df = ods_df

# 1. 去除空格（trim）
dwd_df = dwd_df.withColumn("product", trim(col("product"))) \
               .withColumn("region", trim(col("region"))) \
               .withColumn("customer_name", trim(col("customer_name")))
print("✅ 第1步：去除首尾空格")

# 2. 统一日期格式（2024/01/16 → 2024-01-16）
dwd_df = dwd_df.withColumn("order_date", regexp_replace(col("order_date"), "/", "-"))
print("✅ 第2步：统一日期格式")

# 3. 类型转换（amount 从 STRING 转 INT）
dwd_df = dwd_df.withColumn("amount", col("amount").cast("int"))
print("✅ 第3步：类型转换")

# 4. 数据过滤（去除异常数据）
dwd_df = dwd_df.filter(col("amount") > 0)  # 数量必须大于0
dwd_df = dwd_df.filter(col("price") > 0)    # 价格必须大于0
dwd_df = dwd_df.filter(col("product") != "未知商品")  # 去除未知商品
print("✅ 第4步：过滤异常数据（负数、零值、未知商品）")

# 5. 去重
dwd_df = dwd_df.dropDuplicates(["order_id"])
print("✅ 第5步：按 order_id 去重")

# 6. 添加计算列
dwd_df = dwd_df.withColumn("total_amount", col("amount") * col("price"))
print("✅ 第6步：添加计算列 total_amount")

# 7. 添加数据质量标记
dwd_df = dwd_df.withColumn("data_quality", lit("clean"))
print("✅ 第7步：添加数据质量标记")

# 8. 统一产品名称（标准化）
dwd_df = dwd_df.withColumn("product", 
    when(col("product") == "手机", "智能手机")
    .when(col("product") == "电脑", "笔记本电脑")
    .when(col("product") == "平板", "平板电脑")
    .otherwise(col("product"))
)
print("✅ 第8步：产品名称标准化")

# ========== 展示清洗结果 ==========
print("\n" + "=" * 60)
print("📊 DWD 层清洗后数据")
print("=" * 60)
dwd_df.show(truncate=False)

print("📋 DWD 层表结构:")
dwd_df.printSchema()

print(f"\n📈 数据统计:")
print(f"  ODS 原始记录数: {ods_df.count()}")
print(f"  DWD 清洗后记录数: {dwd_df.count()}")
print(f"  清洗掉 {ods_df.count() - dwd_df.count()} 条异常/重复数据")

# ========== 按维度分析 ==========
print("\n" + "=" * 60)
print("📊 DWD 层维度分析")
print("=" * 60)

print("=== 按产品统计 ===")
dwd_df.groupBy("product").agg(
    {"total_amount": "sum", "order_id": "count"}
).withColumnRenamed("sum(total_amount)", "总销售额") \
 .withColumnRenamed("count(order_id)", "订单数") \
 .orderBy("总销售额", ascending=False) \
 .show()

print("=== 按区域统计 ===")
dwd_df.groupBy("region").agg(
    {"total_amount": "sum", "order_id": "count"}
).withColumnRenamed("sum(total_amount)", "总销售额") \
 .withColumnRenamed("count(order_id)", "订单数") \
 .orderBy("总销售额", ascending=False) \
 .show()

spark.stop()
print("\n🎉 DWD 层数据清洗完成！")
