#!/bin/bash
source ~/.bashrc

echo "=== 停止旧的 Hive 进程 ==="
jps | grep RunJar | awk '{print $1}' | xargs -r kill
sleep 5

echo "=== 启动 Metastore ==="
setsid nohup hive --service metastore > /tmp/metastore.out 2>&1 &
sleep 20

echo "=== 启动 HiveServer2 ==="
setsid nohup hive --service hiveserver2 > /tmp/hiveserver2.out 2>&1 &
sleep 40

echo "=== 10000 端口监听情况 ==="
ss -tln | grep 10000 || echo "WSL 内未监听 10000"

echo "=== RunJar 进程 ==="
jps | grep RunJar
