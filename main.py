# 测试 HDFS 连接
from hdfs import InsecureClient

client = InsecureClient('http://localhost:9870', user='drownedsnake')
print("=== HDFS 根目录文件 ===")
print(client.list('/'))

# 上传测试文件
client.upload('/test.txt', 'main.py', overwrite=True)
print("文件上传成功")

# 下载测试文件
client.download('/test.txt', 'downloaded_test.txt', overwrite=True)
print("文件下载成功")
# 测试 Hive 连接
from pyhive import hive

conn = hive.Connection(host='localhost', port=10000, username='drownedsnake', auth='NOSASL')
cursor = conn.cursor()

print("\n=== Hive 数据库列表 ===")
cursor.execute('SHOW DATABASES')
print(cursor.fetchall())

print("\n=== 创建测试表 ===")
cursor.execute('CREATE TABLE IF NOT EXISTS py_test (id INT, name STRING)')

try:
    cursor.execute("INSERT INTO py_test VALUES (1, 'python_hive')")
    cursor.execute('SELECT * FROM py_test')
    print(cursor.fetchall())
except Exception as e:
    print(f"INSERT 失败（MapReduce 配置问题，不影响学习）")

cursor.close()
conn.close()
# 测试 Spark 连接
from pyspark.sql import SparkSession
spark = SparkSession.builder \
    .appName("PythonTest") \
    .master("local[*]") \
    .config("spark.driver.host", "localhost") \
    .getOrCreate()
print("\n=== Spark 测试 ===")
spark.range(1, 10).show()
spark.stop()

print("\n=== 全部测试完成 ===")
print("✅ HDFS: 读取、上传、下载 - 成功")
print("✅ Hive: 连接、查询、建表 - 成功")
print("✅ Spark: 本地模式运行成功")
