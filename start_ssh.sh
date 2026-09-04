#!/bin/bash
echo "=== 检查 SSH 服务 ==="
if pgrep sshd > /dev/null 2>&1; then
    echo "sshd 已在运行"
    exit 0
fi
if sudo -n true 2>/dev/null; then
    echo "启动 sshd..."
    sudo service ssh start 2>&1
else
    echo "NEED_PASSWORD: 请手动执行 sudo service ssh start"
    exit 1
fi
sleep 2
pgrep sshd > /dev/null && echo "sshd 启动成功" || echo "sshd 启动失败"
