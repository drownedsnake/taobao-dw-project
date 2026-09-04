import os
os.environ["PYTHONIOENCODING"] = "utf-8"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, round as spark_round

spark = SparkSession.builder \
    .appName("DataFrame进阶") \
    .master("local[*]") \
    .config("spark.driver.host", "localhost") \
    .getOrCreate()

# 1. 从 CSV 创建 DataFrame
data = """id,name,age,score,city
1,张三,20,85.5,北京
2,李四,21,90.0,上海
3,王五,22,78.5,北京
4,赵六,20,92.0,广州
5,孙七,21,88.0,上海
6,周八,23,95.0,北京
7,吴九,22,76.0,广州
8,郑十,20,89.0,上海"""

# 写入临时文件
with open('students.csv', 'w', encoding='utf-8') as f:
    f.write(data)

df = spark.read.csv('students.csv', header=True, inferSchema=True)

# 2. 选择列
print("=== 选择 name 和 score 列 ===")
df.select("name", "score").show()

# 3. 添加新列
print("=== 添加等级列 ===")
df.withColumn("grade", when(df.score >= 90, "优秀")
              .when(df.score >= 80, "良好")
              .otherwise("一般")).show()

# 4. 过滤 + 排序
print("=== 北京的学生，按成绩降序 ===")
df.filter(df.city == "北京").orderBy(df.score.desc()).show()

# 5. 分组聚合
print("=== 各城市平均分和人数 ===")
df.groupBy("city").agg(
    {"score": "avg", "id": "count"}
).withColumnRenamed("avg(score)", "avg_score") \
 .withColumnRenamed("count(id)", "count") \
 .show()

# 6. 去重
print("=== 有哪些城市 ===")
df.select("city").distinct().show()

# 7. 写入 Parquet 格式（列式存储，高效）
df.write.mode("overwrite").parquet("students_parquet")
print("✅ 已保存为 Parquet 格式")

# 8. 读取 Parquet
df2 = spark.read.parquet("students_parquet")
print("=== 从 Parquet 读取 ===")
df2.show()

spark.stop()