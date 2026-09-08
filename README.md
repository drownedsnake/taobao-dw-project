# 电商数仓与可视化项目

本仓库包含两条可独立使用的实践路线：原有 Hadoop、Hive、Spark 学习记录，以及新增的可直接复现的 dbt、DuckDB、Airflow、Docker 数据管道。README 只描述仓库中已有代码能够证明的内容。

## 可复现的数据管道

流程为 CSV → DuckDB 原始表 → dbt 清洗与去重 → 月度销售数据集 → dbt 数据质量测试。

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements-modern.txt
python scripts/load_orders.py
dbt build --profiles-dir .
```

`dbt build` 会验证订单号非空且唯一、关键字段非空、销售金额为正。相同输入重复执行时，原始表会被替换，dbt 模型会重新构建，不会造成订单或销售额翻倍。

## Docker 与调度

```bash
docker compose up --build
```

Airflow 页面位于 `http://localhost:8080`。首次启动生成的管理员凭据会显示在容器日志中。`taobao_daily_pipeline` 每天 02:00 执行数据导入与 `dbt build`。

## 数据模型

| 模型 | 粒度 | 作用 |
|---|---|---|
| `raw_orders` | 原始输入行 | 保留导入结果 |
| `stg_orders` | 每个 `order_id` 一行 | 类型转换、清洗、过滤与去重 |
| `fct_orders` | 每个有效订单一行 | 分析事实表 |
| `monthly_sales` | 月份与品类一行 | 订单数、客户数、销量和销售额 |

## 原有 Hadoop / Hive / Spark 内容

仓库保留 `ods.py`、`dwd.py`、Hive 检查脚本、Superset/Python 报表和学习记录。这些文件需要本机 Hadoop/Hive/Spark 环境，并未包含在 Docker 快速复现流程中。

## 本地性能记录

原项目曾在本地记录约 99,457 行业务数据，以及 Spark 1.5 秒、Hive 7 分钟的运行观察。业务数据和对应日志未提交，因此这些数字不作为仓库的自动验证结果。正式展示时应附脱敏输入、运行命令、日志和同一硬件上的重复测量。
