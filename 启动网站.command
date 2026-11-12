#!/bin/bash
# 双击运行：自动准备环境并启动网站，启动后自动打开浏览器。关闭本窗口即停止网站。
cd "$(dirname "$0")"
echo "正在启动非遗传统舞蹈网站（第一次会安装依赖，需要几分钟）……"
(
  for i in $(seq 1 600); do
    if curl -s -o /dev/null http://127.0.0.1:8000/; then open http://127.0.0.1:8000/; break; fi
    sleep 2
  done
) &
bash start.sh
