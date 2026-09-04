from pyhive import hive

# 连接 HiveServer2 —— 和 Superset、PyCharm Database 连的是同一个 10000 端口
conn = hive.Connection(host="localhost", port=10000, username="drownedsnake")
cursor = conn.cursor()

# 拉取 DM 层的月度总览表
cursor.execute("SELECT stat_month, order_cnt, total_qty, total_amount FROM dm.monthly_sales_summary ORDER BY stat_month")

rows = cursor.fetchall()
print(f"共 {len(rows)} 行")
for row in rows[:5]:
    print(row)

cursor.close()
conn.close()