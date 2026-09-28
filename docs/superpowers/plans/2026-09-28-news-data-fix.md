# News Data Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the news list non-empty from existing project data, keep startup idempotent, and support future Excel news imports.

**Architecture:** Put news creation rules in `news/services.py`, call them from a focused Django management command, and invoke that command from `start.sh` only when the active news table is empty. Keep `news.News` as the active model and leave the legacy `origin.News` schema untouched. Route optional Excel news sheets through the same active model.

**Tech Stack:** Django 5.1, SQLite, Django management commands, pandas/openpyxl for optional Excel import, Django TestCase.

---

### Task 1: Project-guide news service

**Files:**
- Create: `news/services.py`
- Create: `news/test_news_data.py`

- [ ] **Step 1: Write failing tests for guide generation**

Create projects with and without introductions, call `seed_project_guides(limit=2, only_if_empty=True)`, and assert that two `news.News` rows are created with `项目导读：` titles, the system author, linked projects, and safe local content. Call it again and assert the count remains two. Add a test proving an existing manually authored news row prevents seeding when `only_if_empty=True`.

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `.venv/bin/python manage.py test news.test_news_data.ProjectGuideSeedTests -v 2`

Expected: import failure because `news.services` does not exist.

- [ ] **Step 3: Implement the minimal service**

Create `get_system_author()` and `seed_project_guides(limit=12, only_if_empty=False)` in `news/services.py`. Use `platform_editor` with an unusable password, select deterministic projects, derive summaries and HTML paragraphs from existing fields, and use `get_or_create(title=...)` so repeated execution does not duplicate rows.

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run: `.venv/bin/python manage.py test news.test_news_data.ProjectGuideSeedTests -v 2`

Expected: all project-guide seed tests pass.

### Task 2: Management command and one-command startup

**Files:**
- Create: `news/management/__init__.py`
- Create: `news/management/commands/__init__.py`
- Create: `news/management/commands/seed_news.py`
- Modify: `news/test_news_data.py`
- Modify: `start.sh`

- [ ] **Step 1: Write failing command tests**

Use `call_command("seed_news", "--limit", "2", "--if-empty")`, assert two rows and a creation message, then call it again and assert a skip message and unchanged count.

- [ ] **Step 2: Run the command tests and verify RED**

Run: `.venv/bin/python manage.py test news.test_news_data.SeedNewsCommandTests -v 2`

Expected: `Unknown command: 'seed_news'`.

- [ ] **Step 3: Implement the command and startup hook**

Add `--limit` and `--if-empty` arguments to the command, delegate to `seed_project_guides`, and print clear created/skipped output. In `start.sh`, run `.venv/bin/python manage.py seed_news --if-empty` after migrations and before `runserver`.

- [ ] **Step 4: Run command tests and shell syntax validation**

Run: `.venv/bin/python manage.py test news.test_news_data.SeedNewsCommandTests -v 2`

Expected: all command tests pass.

Run: `bash -n start.sh`

Expected: exit code 0 with no output.

### Task 3: Excel news import into the active model

**Files:**
- Modify: `news/services.py`
- Modify: `news/test_news_data.py`
- Modify: `origin/management/commands/import_all_data.py`
- Modify: `requirements.txt`

- [ ] **Step 1: Write failing dataframe import tests**

Build a pandas dataframe containing `标题`, `摘要`, `内容`, `类型`, and `项目名称`. Assert `import_news_dataframe()` writes `news.News`, maps `科普类` to `science`, links the named project, and updates rather than duplicates the same title. Add a test proving rows without title or content are reported as errors and skipped.

- [ ] **Step 2: Run importer tests and verify RED**

Run: `.venv/bin/python manage.py test news.test_news_data.NewsImportTests -v 2`

Expected: import failure because `import_news_dataframe` does not exist.

- [ ] **Step 3: Implement import mapping and wire both sheet names**

Add `import_news_dataframe(df)` to `news/services.py` with explicit category mapping, whitespace/NaN cleanup, project lookup, system author, and `(success_count, error_count)` output. Update `import_all_data.py` to import and call this function for the first present sheet among `新闻资讯` and `相关资讯`. Add `pandas` and `openpyxl` to `requirements.txt` so the documented importer is reproducible.

- [ ] **Step 4: Run importer tests and verify GREEN**

Run: `.venv/bin/python manage.py test news.test_news_data.NewsImportTests -v 2`

Expected: all news import tests pass.

### Task 4: Populate and verify the running site

**Files:**
- Modify: `db.sqlite3` through Django ORM only

- [ ] **Step 1: Run the complete news test module**

Run: `.venv/bin/python manage.py test news.test_news_data -v 2`

Expected: all tests pass.

- [ ] **Step 2: Run project checks**

Run: `.venv/bin/python manage.py check`

Expected: `System check identified no issues`.

- [ ] **Step 3: Seed the current database twice**

Run: `.venv/bin/python manage.py seed_news --if-empty`

Expected on first run: 12 project guides created. Expected on second run: skipped because news already exists.

- [ ] **Step 4: Verify list and detail responses**

Run a Django test-client shell command that requests `/news/`, extracts the first news id, then requests `/news/<id>/`.

Expected: both responses return HTTP 200 and the list contains `项目导读：`.

- [ ] **Step 5: Verify the live server**

Restart with `./start.sh`, request `http://127.0.0.1:8000/news/`, and confirm HTTP 200 plus a generated title. Confirm the database still contains 356 projects and 379 inheritors.
