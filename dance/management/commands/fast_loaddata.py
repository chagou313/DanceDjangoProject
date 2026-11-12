"""批量导入 dumpdata 生成的 JSON（保留原有主键）。

Django 自带的 loaddata 逐条保存，每条记录要和数据库往返一到两次；数据库在海外时
几千条记录要跑很久。这里按模型分批 bulk_create，并在最后重置自增序列。
只用于导入到空表（「上传数据到线上.command」会先 flush）。
"""
from collections import defaultdict

from django.core import serializers
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db import connection, transaction


class Command(BaseCommand):
    help = "批量导入 JSON 数据文件（用于把本地数据导入线上空数据库）"

    def add_arguments(self, parser):
        parser.add_argument("fixture", help="dumpdata 导出的 JSON 文件")
        parser.add_argument("--batch-size", type=int, default=500)

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        by_model = defaultdict(list)  # 保留文件中的模型顺序
        m2m_rows = defaultdict(list)  # through 模型 -> 行

        with open(options["fixture"], encoding="utf-8") as fh:
            for item in serializers.deserialize("json", fh, handle_forward_references=True):
                obj = item.object
                by_model[type(obj)].append(obj)
                for field_name, values in (item.m2m_data or {}).items():
                    field = type(obj)._meta.get_field(field_name)
                    through = field.remote_field.through
                    source = field.m2m_field_name() + "_id"
                    target = field.m2m_reverse_field_name() + "_id"
                    for value in values:
                        m2m_rows[through].append(through(**{source: obj.pk, target: value}))

        total = 0
        with transaction.atomic():
            for model, objs in by_model.items():
                model._default_manager.bulk_create(objs, batch_size=batch_size)
                total += len(objs)
                self.stdout.write(f"  {model._meta.label}: {len(objs)}")
            for through, rows in m2m_rows.items():
                through._default_manager.bulk_create(rows, batch_size=batch_size)
                total += len(rows)

            # 主键是显式写入的，需要把各表的自增序列调到当前最大值之后
            models = list(by_model) + list(m2m_rows)
            statements = connection.ops.sequence_reset_sql(no_style(), models)
            if statements:
                with connection.cursor() as cursor:
                    for sql in statements:
                        cursor.execute(sql)

        self.stdout.write(self.style.SUCCESS(f"导入完成，共 {total} 条记录。"))
