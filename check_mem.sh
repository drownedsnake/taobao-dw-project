#!/bin/bash
source ~/.bashrc
echo "=== 总内存 ==="
free -m | head -2
echo ""
echo "=== 内存占用 TOP 15 进程 ==="
ps aux --sort=-%mem | head -16 | awk '{printf "%-8s %-6s %-5s %-5s %s\n", $1, $2, $3, $4, substr($0, index($0,$11), 120)}'
echo ""
echo "=== Java 大进程清单（jps）==="
jps -l
echo ""
echo "=== 是否有残留的计算容器（任务跑完没退出的）==="
jps | grep -E "MRAppMaster|YarnChild" || echo "无残留容器"
echo ""
echo "=== YARN 上是否有未完成的应用 ==="
curl -s -m 10 "http://localhost:8088/ws/v1/cluster/apps" | python3 -c "
import json,sys
d=json.load(sys.stdin)
apps=d.get('apps',{}).get('app',[])
running=[a for a in apps if a['state'] not in ('FINISHED','FAILED','KILLED')]
print('未结束应用数:', len(running))
for a in running:
    print(a['id'], a['state'], a['name'][:50])
" 2>/dev/null
