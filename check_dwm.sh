#!/bin/bash
source ~/.bashrc
echo "=== 1. 所有 YARN 应用的真实状态 ==="
curl -s -m 10 "http://localhost:8088/ws/v1/cluster/apps" | python3 -c "
import json,sys,datetime
d=json.load(sys.stdin)
apps=d.get('apps',{}).get('app',[])
for a in sorted(apps,key=lambda x:-x['startedTime']):
    st=datetime.datetime.fromtimestamp(a['startedTime']/1000).strftime('%H:%M:%S')
    print(st, a['state'], a['finalStatus'], '|', a['name'][:70].replace(chr(13),' ').replace(chr(10),' '))
" 2>/dev/null
echo ""
echo "=== 2. DWS 表目录有没有数据 ==="
hdfs dfs -ls /user/hive/warehouse/dws.db/category_month_stats/ 2>/dev/null || echo "!! 目录为空或不存在"
echo ""
echo "=== 3. hive.log 最后 12 行 ==="
tail -12 /tmp/drownedsnake/hive.log 2>/dev/null
