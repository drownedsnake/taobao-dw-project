#!/bin/bash
source ~/.bashrc

echo "=== 验证 SSH 免密登录 ==="
ssh -o ConnectTimeout=5 -o BatchMode=yes localhost "echo SSH免密正常" || echo "SSH 连接失败"

echo "=== 启动 HDFS ==="
start-dfs.sh 2>&1 | tail -3

echo "=== 启动 YARN ==="
start-yarn.sh 2>&1 | tail -3

sleep 5
echo ""
echo "=== 进程状态 ==="
jps
echo ""
echo "=== 端口监听 ==="
ss -tln | grep -E ':10000|:9000|:9870|:8080'
