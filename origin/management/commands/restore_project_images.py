from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from origin.models import DanceProject


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}


def discover_images(media_root, relative_directory):
    directory = Path(media_root) / relative_directory
    if not directory.is_dir():
        raise CommandError(f"图片目录不存在：{directory}")
    return sorted(
        (
            path
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
        ),
        key=lambda path: (path.stat().st_mtime_ns, path.name),
    )


class Command(BaseCommand):
    help = "按项目 ID 和图片时间顺序恢复 DanceProject.images"

    def add_arguments(self, parser):
        parser.add_argument("--source", default="origin/20260407")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--overwrite", action="store_true")

    def handle(self, *args, **options):
        relative_directory = Path(options["source"])
        projects = list(DanceProject.objects.order_by("id"))
        images = discover_images(settings.MEDIA_ROOT, relative_directory)

        if len(images) < len(projects):
            raise CommandError(
                f"图片数量不足：项目 {len(projects)}，图片 {len(images)}"
            )

        populated = [project for project in projects if project.images]
        if populated and not options["overwrite"]:
            raise CommandError(
                f"已有 {len(populated)} 条图片关联；如需覆盖请显式使用 --overwrite"
            )

        assignments = list(zip(projects, images[: len(projects)]))
        remaining = len(images) - len(assignments)
        self.stdout.write(
            f"项目 {len(projects)}，图片 {len(images)}，"
            f"计划关联 {len(assignments)}，剩余 {remaining}"
        )

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("预演完成，数据库未修改"))
            return

        media_root = Path(settings.MEDIA_ROOT).resolve()
        with transaction.atomic():
            for project, image_path in assignments:
                relative_path = image_path.resolve().relative_to(media_root).as_posix()
                project.images = relative_path
                project.save(update_fields=["images"])

        self.stdout.write(self.style.SUCCESS(f"已关联 {len(assignments)} 个项目"))
