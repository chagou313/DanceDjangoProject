"""确认目标数据库只属于本网站：发现其他网站（例如 mangowit）的数据表时报错退出。

由「上传数据到线上.command」在建表、清空数据之前调用，防止误清空别的网站的数据库。
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "检查目标数据库里是否有不属于本网站的数据表"

    def handle(self, *args, **options):
        expected = set(connection.introspection.django_table_names())
        expected.add("django_migrations")
        existing = set(connection.introspection.table_names())
        extra = sorted(existing - expected)
        if extra:
            shown = "、".join(extra[:8]) + ("……" if len(extra) > 8 else "")
            raise CommandError(
                f"这个数据库里有 {len(extra)} 张不属于本网站的数据表（{shown}），"
                "可能是其他网站（例如 mangowit）正在使用的数据库。为安全起见已停止，没有做任何修改。"
                "请在 Neon 为本网站新建一个项目，换用新的连接字符串。"
            )
        self.stdout.write(self.style.SUCCESS(f"目标数据库检查通过（已有 {len(existing)} 张本网站的数据表）。"))
