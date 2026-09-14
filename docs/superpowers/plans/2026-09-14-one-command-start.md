# One-Command Django Startup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `./start.sh` create a local environment, prepare SQLite, and launch the Django development server without requiring MySQL.

**Architecture:** Django settings select SQLite by default and select MySQL only when `DB_ENGINE=mysql` is explicitly set. A small shell entry point owns environment creation, dependency installation, migrations, and server startup; dependency files separate the default runtime from optional MySQL support.

**Tech Stack:** Bash, Python 3, Django 5.1, SQLite, unittest, Pillow, requests

---

## File map

- Create `tests/__init__.py`: mark startup tests as an importable test package.
- Create `tests/test_startup_config.py`: executable configuration contract tests.
- Modify `DancedjangoProject/settings.py`: environment-driven SQLite/MySQL database selection.
- Create `requirements.txt`: default SQLite runtime dependencies.
- Create `requirements-mysql.txt`: optional MySQL driver dependencies.
- Create `start.sh`: the one-command development launcher.

### Task 1: Define the database configuration contract

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_startup_config.py`
- Modify: `DancedjangoProject/settings.py:1-100`

- [ ] **Step 1: Create the test package and write the failing configuration tests**

Create an empty `tests/__init__.py`, then create `tests/test_startup_config.py`:

```python
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_database_config(**overrides):
    env = os.environ.copy()
    for name in ("DB_ENGINE", "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT"):
        env.pop(name, None)
    env.update(overrides)
    code = (
        "import json; "
        "from DancedjangoProject.settings import DATABASES; "
        "print(json.dumps(DATABASES['default']))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


class DatabaseSettingsTests(unittest.TestCase):
    def test_sqlite_is_the_default_database(self):
        config = load_database_config()
        self.assertEqual(config["ENGINE"], "django.db.backends.sqlite3")
        self.assertEqual(Path(config["NAME"]), PROJECT_ROOT / "db.sqlite3")

    def test_mysql_configuration_comes_from_environment(self):
        config = load_database_config(
            DB_ENGINE="mysql",
            DB_NAME="example_db",
            DB_USER="example_user",
            DB_PASSWORD="example_password",
            DB_HOST="db.internal",
            DB_PORT="3307",
        )
        self.assertEqual(config["ENGINE"], "django.db.backends.mysql")
        self.assertEqual(config["NAME"], "example_db")
        self.assertEqual(config["USER"], "example_user")
        self.assertEqual(config["PASSWORD"], "example_password")
        self.assertEqual(config["HOST"], "db.internal")
        self.assertEqual(config["PORT"], "3307")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest tests/test_startup_config.py -v
```

Expected: `test_sqlite_is_the_default_database` fails because the current default engine is MySQL, and the environment mapping test fails because values are hard-coded.

- [ ] **Step 3: Implement environment-driven database settings**

Add `import os` beside the existing `pathlib` import and replace the current `DATABASES` block with:

```python
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()

if DB_ENGINE == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.getenv("DB_NAME", "dance_platform"),
            "USER": os.getenv("DB_USER", "root"),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "3306"),
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
                "charset": "utf8mb4",
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
```

- [ ] **Step 4: Run the configuration tests and verify GREEN**

Run:

```bash
.venv/bin/python -m unittest tests/test_startup_config.py -v
```

Expected: 2 tests pass.

- [ ] **Step 5: Commit the database configuration change**

```bash
git commit --only tests/__init__.py tests/test_startup_config.py DancedjangoProject/settings.py -m "feat: default local startup to sqlite"
```

### Task 2: Declare reproducible dependencies

**Files:**
- Create: `requirements.txt`
- Create: `requirements-mysql.txt`

- [ ] **Step 1: Write the failing dependency-file contract test**

Add this test class to `tests/test_startup_config.py`:

```python
class DependencyFileTests(unittest.TestCase):
    def test_default_requirements_cover_runtime_imports(self):
        requirements = (PROJECT_ROOT / "requirements.txt").read_text()
        self.assertIn("Django>=5.1,<5.2", requirements)
        self.assertIn("Pillow>=10,<13", requirements)
        self.assertIn("requests>=2.31,<3", requirements)
        self.assertNotIn("mysqlclient", requirements)

    def test_mysql_requirements_extend_default_requirements(self):
        requirements = (PROJECT_ROOT / "requirements-mysql.txt").read_text()
        self.assertIn("-r requirements.txt", requirements)
        self.assertIn("mysqlclient>=2.2,<3", requirements)
```

- [ ] **Step 2: Run the dependency tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_startup_config.DependencyFileTests -v
```

Expected: errors report that `requirements.txt` and `requirements-mysql.txt` do not exist.

- [ ] **Step 3: Create the dependency files**

Create `requirements.txt`:

```text
Django>=5.1,<5.2
Pillow>=10,<13
requests>=2.31,<3
```

Create `requirements-mysql.txt`:

```text
-r requirements.txt
mysqlclient>=2.2,<3
```

- [ ] **Step 4: Run the complete configuration test file**

Run:

```bash
.venv/bin/python -m unittest tests/test_startup_config.py -v
```

Expected: 4 tests pass.

- [ ] **Step 5: Commit dependency declarations**

```bash
git commit --only requirements.txt requirements-mysql.txt tests/test_startup_config.py -m "build: declare django runtime dependencies"
```

### Task 3: Add the one-command launcher

**Files:**
- Modify: `tests/test_startup_config.py`
- Create: `start.sh`

- [ ] **Step 1: Write the failing launcher contract tests**

Add this test class to `tests/test_startup_config.py`:

```python
class StartScriptTests(unittest.TestCase):
    def test_start_script_is_executable_and_has_valid_bash_syntax(self):
        script = PROJECT_ROOT / "start.sh"
        self.assertTrue(script.exists())
        self.assertTrue(os.access(script, os.X_OK))
        subprocess.run(["bash", "-n", script], check=True)

    def test_start_script_prepares_and_runs_django(self):
        script = (PROJECT_ROOT / "start.sh").read_text()
        self.assertIn("-m venv", script)
        self.assertIn("-m pip install -r requirements.txt", script)
        self.assertIn("manage.py migrate --noinput", script)
        self.assertIn("manage.py runserver", script)
        self.assertIn('${HOST:-127.0.0.1}:${PORT:-8000}', script)
```

- [ ] **Step 2: Run the launcher tests and verify RED**

Run:

```bash
.venv/bin/python -m unittest tests.test_startup_config.StartScriptTests -v
```

Expected: failures report that `start.sh` does not exist.

- [ ] **Step 3: Create the launcher**

Create executable `start.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "错误：找不到 $PYTHON_BIN，请先安装 Python 3。" >&2
    exit 1
fi

if [[ ! -x .venv/bin/python ]]; then
    "$PYTHON_BIN" -m venv .venv
fi

.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate --noinput

echo "项目已准备完成：http://${HOST:-127.0.0.1}:${PORT:-8000}"
exec .venv/bin/python manage.py runserver "${HOST:-127.0.0.1}:${PORT:-8000}" --noreload
```

Set its executable bit:

```bash
chmod +x start.sh
```

- [ ] **Step 4: Run all startup contract tests and verify GREEN**

Run:

```bash
.venv/bin/python -m unittest tests/test_startup_config.py -v
```

Expected: 6 tests pass.

- [ ] **Step 5: Commit the launcher**

```bash
git commit --only start.sh tests/test_startup_config.py -m "feat: add one-command django launcher"
```

### Task 4: Verify the complete startup path

**Files:**
- Verify only; no new production files.

- [ ] **Step 1: Run the full test suite and Django self-check**

Run:

```bash
.venv/bin/python -m unittest tests/test_startup_config.py -v
.venv/bin/python manage.py check
```

Expected: 6 startup tests pass and Django reports `System check identified no issues (0 silenced).`

- [ ] **Step 2: Start through the public command**

Run:

```bash
PORT=8765 ./start.sh
```

Expected: dependencies are satisfied, migrations finish successfully, and Django listens at `http://127.0.0.1:8765/`.

- [ ] **Step 3: Verify representative routes**

In a second terminal, run:

```bash
for path in / /news/ /origin/ /knowledge/ /quiz/ /login/ /admin/; do
    curl -sS -o /dev/null -w "$path HTTP %{http_code}\n" "http://127.0.0.1:8765$path"
done
```

Expected: public routes return HTTP 200 and `/admin/` returns HTTP 302 to its login page.

- [ ] **Step 4: Stop the development server**

Press `Ctrl-C` in the server terminal and confirm it exits without leaving a listener on port 8765.
