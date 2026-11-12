#!/bin/bash
# 双击运行：把本机的数据库内容导入线上 Neon 数据库，并把图片上传到 Cloudinary。
# 需要先在本文件夹放好 .env.deploy（格式见 .env.example 末尾）。
set -euo pipefail
cd "$(dirname "$0")"

finish() { echo; read -r -p "按回车键关闭窗口" _; }
trap finish EXIT

if [[ ! -f .env.deploy ]]; then
    echo "缺少 .env.deploy 文件。请在本文件夹新建它，写入两行："
    echo "  DATABASE_URL=postgresql://...（Neon 的连接字符串）"
    echo "  CLOUDINARY_URL=cloudinary://...（Cloudinary 的连接字符串）"
    exit 1
fi
if [[ ! -f db.sqlite3 ]]; then
    echo "缺少本地数据库 db.sqlite3。"
    exit 1
fi

PY=.venv/bin/python
[[ -x "$PY" ]] || python3 -m venv .venv
echo "准备运行环境……"
"$PY" -m pip install -q -r requirements.txt

DUMP="${TMPDIR:-/tmp}/dance_data_$$.json"
echo "1/4 从本地数据库导出数据……"
env -u DATABASE_URL -u CLOUDINARY_URL "$PY" manage.py dumpdata \
    --natural-foreign --natural-primary \
    -e contenttypes -e auth.permission -e sessions -e admin.logentry \
    -o "$DUMP"

set -a
# shellcheck disable=SC1091
source .env.deploy
set +a
if [[ -z "${DATABASE_URL:-}" || -z "${CLOUDINARY_URL:-}" ]]; then
    echo ".env.deploy 里需要同时有 DATABASE_URL 和 CLOUDINARY_URL。"
    exit 1
fi

echo "2/4 在线上数据库创建数据表……"
"$PY" manage.py migrate --noinput

USERS=$("$PY" manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())" | tail -1)
if [[ "$USERS" != "0" ]]; then
    echo "线上数据库里已经有 $USERS 个用户。继续会清空线上数据库，再用本机数据重新导入。"
    read -r -p "确定要继续吗？输入 yes 继续：" ANSWER
    [[ "$ANSWER" == "yes" ]] || { echo "已取消。"; exit 1; }
fi
"$PY" manage.py flush --noinput

echo "3/4 导入数据……"
"$PY" manage.py loaddata "$DUMP"
rm -f "$DUMP"

echo "4/4 上传图片和视频到 Cloudinary（约 400 个文件，需要几分钟）……"
"$PY" manage.py upload_media_to_cloudinary

echo
echo "全部完成。现在可以去 Render 部署网站了。"
