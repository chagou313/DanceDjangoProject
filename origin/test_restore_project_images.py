import os
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from origin.models import DanceProject


class RestoreProjectImagesCommandTests(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.media_root = Path(self.temp_dir.name)
        self.image_dir = self.media_root / "origin" / "20260407"
        self.image_dir.mkdir(parents=True)
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root)
        self.settings_override.enable()

    def tearDown(self):
        self.settings_override.disable()
        self.temp_dir.cleanup()

    def create_project(self, name):
        return DanceProject.objects.create(project_code="III-1", name=name)

    def create_image(self, name, timestamp):
        path = self.image_dir / name
        path.write_bytes(b"image")
        os.utime(path, ns=(timestamp, timestamp))
        return path

    def test_dry_run_reports_counts_without_writing(self):
        first = self.create_project("First")
        second = self.create_project("Second")
        self.create_image("later.png", 2_000_000_000)
        self.create_image("earlier.png", 1_000_000_000)
        self.create_image("unused.png", 3_000_000_000)
        stdout = StringIO()

        call_command("restore_project_images", dry_run=True, stdout=stdout)

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.images)
        self.assertFalse(second.images)
        self.assertIn("项目 2，图片 3，计划关联 2，剩余 1", stdout.getvalue())

    def test_assigns_projects_by_id_and_images_by_time_then_name(self):
        first = self.create_project("First")
        second = self.create_project("Second")
        self.create_image("same-time-b.png", 1_000_000_000)
        self.create_image("same-time-a.png", 1_000_000_000)

        call_command("restore_project_images", stdout=StringIO())

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(first.images.name, "origin/20260407/same-time-a.png")
        self.assertEqual(second.images.name, "origin/20260407/same-time-b.png")

    def test_rejects_insufficient_images_without_partial_updates(self):
        first = self.create_project("First")
        second = self.create_project("Second")
        self.create_image("only.png", 1_000_000_000)

        with self.assertRaisesMessage(CommandError, "图片数量不足"):
            call_command("restore_project_images", stdout=StringIO())

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertFalse(first.images)
        self.assertFalse(second.images)

    def test_refuses_to_overwrite_existing_association_by_default(self):
        project = self.create_project("First")
        project.images = "origin/existing.png"
        project.save(update_fields=["images"])
        self.create_image("replacement.png", 1_000_000_000)

        with self.assertRaisesMessage(CommandError, "已有 1 条图片关联"):
            call_command("restore_project_images", stdout=StringIO())

        project.refresh_from_db()
        self.assertEqual(project.images.name, "origin/existing.png")

    def test_overwrite_option_replaces_existing_association(self):
        project = self.create_project("First")
        project.images = "origin/existing.png"
        project.save(update_fields=["images"])
        self.create_image("replacement.png", 1_000_000_000)

        call_command("restore_project_images", overwrite=True, stdout=StringIO())

        project.refresh_from_db()
        self.assertEqual(
            project.images.name,
            "origin/20260407/replacement.png",
        )
