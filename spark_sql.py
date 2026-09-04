import findspark

findspark.init()
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("结果") \
    .config("spark.driver.host", "127.0.0.1") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

df = spark.read.csv("C:\\Users\\drownedsnake\\PycharmProjects\\PythonProject1\\sales.csv", header=True, inferSchema=True,
                    encoding="UTF-8")
df.show(2)

df.createOrReplaceTempView("sales")

result = spark.sql("SELECT * FROM sales")
result.show()

spark.stop()
