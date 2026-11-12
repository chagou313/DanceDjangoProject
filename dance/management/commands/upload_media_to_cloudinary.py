"""把本地 media/ 里被数据库引用的图片和视频上传到 Cloudinary，并更新数据库里的文件名。

在设置了 DATABASE_URL（线上数据库）和 CLOUDINARY_URL 的环境里运行。
已上传过的文件会跳过，可以重复运行。
"""
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import models


class Command(BaseCommand):
    help = "上传本地 media 文件到 Cloudinary，并把数据库中的文件路径换成 Cloudinary 地址"

    def add_arguments(self, parser):
        parser.add_argument("--media-root", default=str(settings.MEDIA_ROOT), help="本地 media 文件夹")

    def handle(self, *args, **options):
        if not getattr(settings, "USE_CLOUDINARY", False):
            raise CommandError("没有设置 CLOUDINARY_URL，无法上传。")

        media_root = Path(options["media_root"])
        prefix = settings.CLOUDINARY_STORAGE["PREFIX"].strip("/") + "/"
        uploaded = skipped = missing = 0

        for model in apps.get_models():
            file_fields = [f for f in model._meta.get_fields() if isinstance(f, models.FileField)]
            for field in file_fields:
                rows = (
                    model._default_manager.exclude(**{field.name: ""})
                    .exclude(**{f"{field.name}__isnull": True})
                    .values_list("pk", field.name)
                )
                for pk, name in rows:
                    if name.startswith(prefix):
                        skipped += 1
                        continue
                    local_path = media_root / name
                    if not local_path.is_file():
                        missing += 1
                        self.stderr.write(f"  找不到本地文件，已跳过：{model.__name__}#{pk} {name}")
                        continue
                    with local_path.open("rb") as fh:
                        new_name = field.storage.save(name, File(fh, name=local_path.name))
                    model._default_manager.filter(pk=pk).update(**{field.name: new_name})
                    uploaded += 1
                    if uploaded % 20 == 0:
                        self.stdout.write(f"  已上传 {uploaded} 个文件……")

        self.stdout.write(self.style.SUCCESS(
            f"完成：上传 {uploaded} 个，之前已上传 {skipped} 个，缺少本地文件 {missing} 个。"
        ))
