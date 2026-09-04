# 基于 Hadoop + Hive 的电商用户行为数仓与可视化平台

> 从零搭建单节点大数据集群，落地 5 层数仓，打通 Superset / Python 双可视化路线，并用 Spark 与维度建模完成进阶——一份完整的离线数仓实战记录。

维护者：[@drownedsnake](https://github.com/drownedsnake)


## 一、项目背景

- **数据集**：淘宝用户行为订单数据，99,457 行 × 9 列（订单号、客户、性别、年龄、品类、数量、单价、支付方式、日期），覆盖 2021-01 ~ 2023-03 共 39 个月
- **环境**：Windows 11 + WSL2 Ubuntu 22.04 单节点，8GB 内存
- **目标**：完整走通"原始文件 → 数据入仓 → 分层加工 → 报表可视化"的企业级数据链路

## 二、技术栈

| 类别 | 组件 | 版本 |
|---|---|---|
| 存储/调度 | Hadoop（HDFS + YARN + MapReduce） | 3.3.6 |
| 数仓引擎 | Hive（Metastore 后端 MySQL 8.0） | 3.1.3 |
| 计算引擎 | Spark（Standalone） | 3.5.1 |
| BI 工具 | Apache Superset | 6.1.0 |
| 开发端 | PyCharm + PyHive + pyecharts | Python 3.12 / 3.10 |
| 接入协议 | Thrift / SASL / JDBC | — |

## 三、总体架构

```
              淘宝订单 CSV（99,457 行）
                    │  预处理（sed 去尾逗号 / cut 裁异常列）
                    ▼
                ┌─────── HDFS ───────┐
                │                    │
     ┌──────────┴────── Hive 数仓 ────┴──────────┐
     │  ODS 原始层（全 STRING、外部表、跳表头）      │
     │  DWD 明细层（8 步清洗、ORC 列存）            │
     │  DWM 汇总层（用户×天 粒度）                  │
     │  DWS 主题层（品类×月 统计）                  │
     │  DM  集市层（华为规范，报表直供，≈阿里 ADS）  │
     │  dim 维度层（品类维表/客户维表，星型模型）     │
     └──────────┬─────────────────┬──────────────┘
          B 路线│                 │A 路线
     ┌──────────▼──────┐  ┌───────▼────────────┐
     │ Superset 看板    │  │ PyHive + pyecharts │
     │ (拖拽、实时查询)  │  │ (代码、定时自动化)  │
     └─────────────────┘  └────────────────────┘
          进阶：Spark 清洗（1.5s vs MR 7min）/ 维度建模 / 任务计划程序
```

## 四、数仓分层设计

| 层 | 表 | 职责 | 要点 |
|---|---|---|---|
| ODS | `taobao_user_behavior` | 原始贴源 | 外部表 + 全 STRING + `skip.header.line.count` |
| DWD | `taobao_user_behavior_clean` | 清洗标准化 | 8 步清洗法：去空格、日期标准化（`2021/4/17`→`2021-04-17`）、`round` 消浮点噪声（16% 的行受影响）、类型转换、过滤异常；ORC 存储 |
| DWM | `customer_day_purchase` | 轻度汇总 | 用户×天 粒度，订单数/件数/金额 |
| DWS | `category_month_stats` 等 | 主题聚合 | 品类×月，必须从 DWD 建（DWM 已丢失品类维度） |
| DM | `monthly_sales_summary`、`monthly_category_rank` | 报表直供 | 华为规范命名（对标阿里 ADS）；`COUNT(DISTINCT)` 不能二次汇总，客户数必须回明细重算 |
| dim | `dim_product_category`、`dim_customer` | 维度建模 | 星型模型；`ROW_NUMBER()` 造代理键；`CASE WHEN` 派生年龄段 |

## 五、性能实测数据

| 指标 | 数值 |
|---|---|
| DWD 清洗（Hive MR） | ~7 分钟 |
| **DWD 清洗（Spark，同逻辑）** | **1.5 秒（快 ~280 倍）** |
| ODS 行数 | 99,457 |
| 品类维表 | 8 行（代理键 1~8） |
| 月度指标 | 39 个月 |
| 存储对比（9.9 万行） | CSV 6.07MB → ORC 1.39MB / Parquet 1.61MB |

## 六、踩坑记录（精华 15 条）

### 环境与网络

| # | 现象 | 根因 | 解法 |
|---|---|---|---|
| 1 | HiveServer2 起不来，10000 端口无监听 | 百度网盘 `YunDetectService.exe` 抢占 10000 端口（WSL2 镜像模式共享端口空间） | 结束占用进程后重启；排查口径：`ss -tlnp` 看监听归属 |
| 2 | JDBC 连接报 SASL 握手失败 | WSL2 localhost 端口转发代理破坏 SASL 流 | 切换镜像网络模式，localhost 直连 |
| 3 | venv 创建失败 | Ubuntu 拆包习惯，缺 `python3.10-venv` | `apt install python3.10-venv` |
| 4 | 编译 `sasl` 报缺 `Python.h` | 缺 `python3.10-dev` 头文件 | 补装后重编译 |

### 计算引擎

| # | 现象 | 根因 | 解法 |
|---|---|---|---|
| 5 | `return code 2 from MapRedTask`，YARN 无任务 | `hive.exec.mode.local.auto=true` 把任务路由进 HiveServer2 的 256MB 小堆 → OOM | 删除该配置；`HADOOP_HEAPSIZE=1024` |
| 6 | MR 任务提交后容器秒挂 | tarball 安装缺 `mapreduce.application.classpath`，MRAppMaster 找不到 jar | 在 `mapred-site.xml` 写死绝对路径类路径 |
| 7 | INSERT 执行中报 Connection reset | 客户端断连导致任务被 KILL；表预览与长任务抢连接 | 避免并发预览；重连后任务自动重新提交 |
| 8 | PySpark 报 `NOT_COLUMN_OR_STR, got float` | `from pyspark.sql.functions import round` 覆盖内置 `round`（或反之） | 别名导入 / `import pyspark.sql.functions as F` |

### 客户端与工具

| # | 现象 | 根因 | 解法 |
|---|---|---|---|
| 9 | PyCharm 报"无法解析表" | IDE 元数据缓存未刷新 | Refresh 数据源；波浪线 ≠ 执行错误 |
| 10 | 建库语句"消失" | `Ctrl+Enter` 只执行光标所在语句 | 逐条核对或全选执行（两次中招） |
| 11 | `Table not found` 但表存在 | 库名假设错误（阿里 `ads` ≠ 用户的华为 `dm`） | 写 SQL 前先 `SHOW DATABASES` 验证 |
| 12 | Superset 启动/查询 500 | 6.1.0 漏打包 `rich`/`cachetools`/`thrift_sasl` 等依赖 | 看 Traceback 缺啥补啥 |
| 13 | Superset 图表查询被掐 | 默认 60s 超时 < MR 耗时 | 外部配置文件双参数放宽到 300s |
| 14 | 双击 HTML 报"找不到 chrome" | 系统默认浏览器指向已卸载程序 | 重设 .html 文件关联到 Edge |
| 15 | 定时任务文件写丢 | 任务计划程序未填"起始于" | 必须指定工作目录 |

## 七、核心经验沉淀

1. **四种慢要分清**：MR 启动税（30s 起步）/ 单机资源挤兑 / 客户端收尾探测 / 假转圈——单节点学习环境的慢不等于架构的慢
2. **先探查后清洗**：数据体检（6 项指标）发现 16% 浮点噪声，清洗规则才有依据
3. **聚合不可逆**：`COUNT(DISTINCT)` 不能二次汇总；DWM 压粒度会丢维度，主题表要回明细建
4. **直觉要验证**：星型查询推翻"年轻人是主力"的预设——50+ 人群才是消费榜首
5. **列式三件套**：列裁剪 + 谓词下推 + 压缩存储，Parquet/ORC 按计算引擎生态选
6. **自动化三要素**：幂等（文件名带时间戳）+ 依赖检查（集群在线）+ 失败可观测（任务历史 0x0）

## 八、快速复现

```bash
# 1. 启动集群（WSL）
start-dfs.sh && start-yarn.sh
$SPARK_HOME/sbin/start-all.sh
bash restart_hive.sh          # Metastore + HiveServer2

# 2. Superset（WSL）
source ~/superset-env/bin/activate
export SUPERSET_CONFIG_PATH=$HOME/superset_config.py
superset run -p 8089 --with-threads

# 3. 报表脚本（Windows）
python sales_chart.py         # 生成 sales_report_YYYYMMDD.html
```

## 九、项目文件

| 文件 | 说明 |
|---|---|
| `dm_test.py` | PyHive 连接 DM 层的最小验证脚本 |
| `sales_chart.py` | 双图报表生成（月度趋势 + 品类排行，pyecharts Page） |
| `sales_report_*.html` | 生成的交互式报表（按日期存档） |
| `restart_hive.sh` | Hive 服务重启脚本 |
| `make_ppt.py` | 项目总结 PPT 生成脚本（python-pptx） |
