import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_database_config(**overrides):
    env = os.environ.copy()
    for name in (
        "DB_ENGINE",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
        "DB_PORT",
    ):
        env.pop(name, None)
    env.update(overrides)
    code = (
        "import json; "
        "from DancedjangoProject.settings import DATABASES; "
        "print(json.dumps(DATABASES['default'], default=str))"
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


if __name__ == "__main__":
    unittest.main()
