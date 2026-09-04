import page
from pyhive import hive
from pyecharts.charts import Line, Bar, Page
from pyecharts import options as opts

# ---- 第 1 步：一次连接，查两张表 ----
conn = hive.Connection(host="localhost", port=10000, username="drownedsnake")
cursor = conn.cursor()

# 图1 数据：月度趋势（老朋友）
cursor.execute("SELECT stat_month, total_amount FROM dm.monthly_sales_summary ORDER BY stat_month")
trend_rows = cursor.fetchall()

# 图2 数据：品类总销售额（现算的聚合，直接从明细层 GROUP BY）
cursor.execute("""
    SELECT category, ROUND(SUM(quantity * price), 2) AS total
    FROM dwd.taobao_user_behavior_clean
    GROUP BY category
    ORDER BY total DESC
""")
category_rows = cursor.fetchall()

cursor.close()
conn.close()

# ---- 第 2 步：整理数据 ----
months = [r[0] for r in trend_rows]
amounts = [round(float(r[1]) / 10000, 2) for r in trend_rows]
categories = [r[0] for r in category_rows]
cat_totals = [round(float(r[1]) / 10000, 2) for r in category_rows]

# ---- 第 3 步：两张图 ----
line = (
    Line()
    .add_xaxis(months)
    .add_yaxis("月销售额（万元）", amounts, is_smooth=True)
    .set_global_opts(title_opts=opts.TitleOpts(title="月度销售趋势"))
)

bar = (
    Bar()
    .add_xaxis(categories)
    .add_yaxis("总销售额（万元）", cat_totals)
    .set_global_opts(title_opts=opts.TitleOpts(title="品类销售额排行"))
)

# ---- 第 4 步：Page 组装成报告页 ----
from datetime import datetime

today = datetime.now().strftime("%Y%m%d")
out_file = f"sales_report_{today}.html"
page = Page(layout=Page.SimplePageLayout)
page.add(line, bar)
page.render(out_file)
page.render(out_file)
print(f"报告已生成：{out_file}（趋势 {len(months)} 个月，品类 {len(categories)} 个）")