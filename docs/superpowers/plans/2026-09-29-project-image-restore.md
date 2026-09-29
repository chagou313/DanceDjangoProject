# Project Image Restoration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore one stable media path to each of the 356 existing dance projects while preserving the existing Django model, templates, media files, and unrelated user changes.

**Architecture:** Add one focused Django management command that discovers image files deterministically, validates the database state, supports dry-run and explicit overwrite modes, and applies assignments inside one transaction. Test the command through Django's public `call_command` interface using a temporary media directory, then back up and update the real SQLite database.

**Tech Stack:** Python 3, Django 5.1, Django `TestCase`, SQLite, `pathlib`

---

## File Structure

- Create `origin/management/__init__.py`: marks the management directory as a Python package.
- Create `origin/management/commands/__init__.py`: marks the commands directory as a Python package.
- Create `origin/management/commands/restore_project_images.py`: contains deterministic discovery, validation, dry-run reporting, and transactional image assignment.
- Create `origin/test_restore_project_images.py`: isolates command behavior tests from the user's existing modified `origin/tests.py`.
- Create `db.sqlite3.before_project_image_restore_20260929`: runtime backup made immediately before the production write; it remains untracked.

### Task 1: Specify image discovery and dry-run behavior

**Files:**
- Create: `origin/test_restore_project_images.py`

- [ ] **Step 1: Write failing tests for deterministic discovery and dry-run**

```python
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
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```bash
python3 manage.py test origin.test_restore_project_images -v 2
```

Expected: all five tests fail with `Unknown command: 'restore_project_images'`.

- [ ] **Step 3: Commit only the failing behavioral specification**

```bash
git add origin/test_restore_project_images.py
git commit -m "test: specify project image restoration"
```

### Task 2: Implement the minimal restoration command

**Files:**
- Create: `origin/management/__init__.py`
- Create: `origin/management/commands/__init__.py`
- Create: `origin/management/commands/restore_project_images.py`
- Test: `origin/test_restore_project_images.py`

- [ ] **Step 1: Add the command packages and minimal implementation**

Create empty `origin/management/__init__.py` and `origin/management/commands/__init__.py`, then create:

```python
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
```

- [ ] **Step 2: Run the focused tests and verify GREEN**

Run:

```bash
python3 manage.py test origin.test_restore_project_images -v 2
```

Expected: 5 tests pass.

- [ ] **Step 3: Commit the minimal command**

```bash
git add origin/management/__init__.py origin/management/commands/__init__.py origin/management/commands/restore_project_images.py
git commit -m "feat: restore project image paths"
```

### Task 3: Back up and restore the real SQLite database

**Files:**
- Create: `db.sqlite3.before_project_image_restore_20260929` (untracked backup)
- Modify: `db.sqlite3` (runtime data only)

- [ ] **Step 1: Run Django configuration checks and the full relevant test suite**

Run:

```bash
python3 manage.py check
python3 manage.py test origin.test_restore_project_images origin.tests news.tests -v 2
```

Expected: system check reports no issues and all selected tests pass.

- [ ] **Step 2: Run a production dry-run**

Run:

```bash
python3 manage.py restore_project_images --dry-run
```

Expected: `项目 356，图片 365，计划关联 356，剩余 9` and `数据库未修改`.

- [ ] **Step 3: Verify the backup target is unused, then copy SQLite**

Run:

```bash
test ! -e db.sqlite3.before_project_image_restore_20260929
cp -p db.sqlite3 db.sqlite3.before_project_image_restore_20260929
```

Expected: both commands exit successfully and the backup file exists.

- [ ] **Step 4: Execute the restoration once**

Run:

```bash
python3 manage.py restore_project_images
```

Expected: `已关联 356 个项目`.

- [ ] **Step 5: Verify database and filesystem consistency independently**

Run:

```bash
python3 manage.py shell -c "from pathlib import Path; from django.conf import settings; from origin.models import DanceProject; qs=DanceProject.objects.exclude(images__isnull=True).exclude(images=''); missing=[p.images.name for p in qs if not (Path(settings.MEDIA_ROOT)/p.images.name).is_file()]; print({'total': DanceProject.objects.count(), 'with_images': qs.count(), 'missing_files': len(missing)})"
```

Expected:

```text
{'total': 356, 'with_images': 356, 'missing_files': 0}
```

### Task 4: Verify the running website serves restored images

**Files:**
- No source changes expected.

- [ ] **Step 1: Request a project page and one restored media URL**

Run:

```bash
curl -fsS http://127.0.0.1:8000/ -o /tmp/dance-home-after-image-restore.html
TASK_MEDIA_URL="$(python3 manage.py shell -c "from origin.models import DanceProject; print(DanceProject.objects.order_by('id').first().images.url)")"
curl -I "http://127.0.0.1:8000${TASK_MEDIA_URL}"
```

Expected: the home request succeeds and the media request returns HTTP 200 with an image content type.

- [ ] **Step 2: Re-run the command without overwrite to prove repeat safety**

Run:

```bash
python3 manage.py restore_project_images
```

Expected: command exits with `已有 356 条图片关联；如需覆盖请显式使用 --overwrite` and changes no rows.

- [ ] **Step 3: Review only task-owned source changes**

Run:

```bash
git diff HEAD -- origin/management/__init__.py origin/management/commands/__init__.py origin/management/commands/restore_project_images.py origin/test_restore_project_images.py
git status --short
```

Expected: only the intended new command/test files are task-owned; the user's pre-existing modified, renamed, and untracked files remain present and untouched.
