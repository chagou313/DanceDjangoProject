from django.core.management.base import BaseCommand

from news.services import seed_project_guides


class Command(BaseCommand):
    help = "根据现有舞蹈项目生成幂等的站内项目导读"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=12)
        parser.add_argument("--if-empty", action="store_true")

    def handle(self, *args, **options):
        created_count, skipped = seed_project_guides(
            limit=options["limit"],
            only_if_empty=options["if_empty"],
        )
        if skipped:
            self.stdout.write("新闻数据已存在，跳过初始化。")
            return
        if created_count == 0:
            self.stdout.write("没有可创建的项目导读。")
            return
        self.stdout.write(self.style.SUCCESS(f"已创建 {created_count} 条项目导读。"))
