#!/bin/bash
source ~/.bashrc

echo "=== 0. 检查 MySQL（如未运行请先手动: sudo service mysql start）==="
if pgrep mysqld > /dev/null 2>&1; then
    echo "MySQL 已在运行"
else
    echo "⚠ MySQL 未运行！请先在 WSL 终端执行: sudo service mysql start"
    exit 1
fi

echo "=== 1. 启动 HDFS ==="
start-dfs.sh 2>&1 | tail -3

echo "=== 2. 启动 YARN ==="
start-yarn.sh 2>&1 | tail -3

echo "=== 3. 启动 Hive Metastore ==="
setsid nohup hive --service metastore > /tmp/metastore.out 2>&1 &
disown
sleep 20

echo "=== 4. 启动 HiveServer2 ==="
setsid nohup hive --service hiveserver2 > /tmp/hiveserver2.out 2>&1 &
disown
sleep 30

echo "=== 5. 启动 Spark ==="
start-master.sh 2>&1 | tail -1
start-worker.sh spark://localhost:7077 2>&1 | tail -1

echo ""
echo "=== 进程状态 ==="
jps
echo ""
echo "=== 端口监听 ==="
ss -tln | grep -E ':10000|:9000|:9870|:8080' 
