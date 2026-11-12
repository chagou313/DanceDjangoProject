from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from origin.excel_import import import_all_from_excel


class Command(BaseCommand):
    help = "从 Excel 导入舞蹈项目、传承人、相关项目和新闻资讯（默认 data/traditional_dance_data.xlsx）"

    def add_arguments(self, parser):
        parser.add_argument(
            "excel_path",
            nargs="?",
            default=str(Path(settings.BASE_DIR) / "data" / "traditional_dance_data.xlsx"),
            help="Excel 文件路径",
        )

    def handle(self, *args, **options):
        import_all_from_excel(options["excel_path"])
