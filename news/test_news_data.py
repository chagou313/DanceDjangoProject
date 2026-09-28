from io import StringIO

import pandas as pd
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from news.models import News
from news.services import get_system_author, import_news_dataframe, seed_project_guides
from origin.models import DanceProject


class ProjectGuideSeedTests(TestCase):
    def setUp(self):
        self.first_project = DanceProject.objects.create(
            project_code="TEST-1",
            name="测试舞蹈甲",
            full_name="测试舞蹈甲",
            declare_region="测试地区甲",
            introduction="甲项目用于验证项目导读内容。",
        )
        self.second_project = DanceProject.objects.create(
            project_code="TEST-2",
            name="测试舞蹈乙",
            full_name="测试舞蹈乙",
            declare_region="测试地区乙",
            introduction="<script>alert('unsafe')</script>乙项目简介。",
        )

    def test_seed_creates_project_guides_from_local_project_data(self):
        created_count, skipped = seed_project_guides(limit=2, only_if_empty=True)

        self.assertEqual(created_count, 2)
        self.assertFalse(skipped)
        self.assertEqual(News.objects.count(), 2)

        first_news = News.objects.get(title="项目导读：测试舞蹈甲")
        self.assertEqual(first_news.author.username, "platform_editor")
        self.assertEqual(first_news.dance_project, self.first_project)
        self.assertIn("甲项目用于验证项目导读内容", first_news.content)

        second_news = News.objects.get(title="项目导读：测试舞蹈乙")
        self.assertNotIn("<script>", second_news.content)
        self.assertIn("&lt;script&gt;", second_news.content)

    def test_seed_is_idempotent(self):
        seed_project_guides(limit=2, only_if_empty=True)
        created_count, skipped = seed_project_guides(limit=2, only_if_empty=True)

        self.assertEqual(created_count, 0)
        self.assertTrue(skipped)
        self.assertEqual(News.objects.count(), 2)

    def test_if_empty_preserves_existing_news(self):
        News.objects.create(
            title="已有资讯",
            summary="已有摘要",
            content="已有正文",
            category="science",
            author=get_system_author(),
        )

        created_count, skipped = seed_project_guides(limit=2, only_if_empty=True)

        self.assertEqual(created_count, 0)
        self.assertTrue(skipped)
        self.assertEqual(list(News.objects.values_list("title", flat=True)), ["已有资讯"])
        self.assertEqual(User.objects.filter(username="platform_editor").count(), 1)


class SeedNewsCommandTests(TestCase):
    def setUp(self):
        DanceProject.objects.create(
            project_code="CMD-1",
            name="命令测试舞蹈",
            introduction="用于验证新闻初始化命令。",
        )

    def test_command_creates_news_then_skips_existing_data(self):
        first_output = StringIO()
        call_command(
            "seed_news",
            "--limit",
            "2",
            "--if-empty",
            stdout=first_output,
        )

        self.assertEqual(News.objects.count(), 1)
        self.assertIn("已创建 1 条项目导读", first_output.getvalue())

        second_output = StringIO()
        call_command(
            "seed_news",
            "--limit",
            "2",
            "--if-empty",
            stdout=second_output,
        )

        self.assertEqual(News.objects.count(), 1)
        self.assertIn("新闻数据已存在，跳过初始化", second_output.getvalue())


class NewsImportTests(TestCase):
    def setUp(self):
        self.project = DanceProject.objects.create(
            project_code="IMPORT-1",
            name="导入测试舞蹈",
            introduction="导入测试项目简介。",
        )

    def test_import_creates_and_updates_active_news_model(self):
        first_data = pd.DataFrame(
            [
                {
                    "标题": "导入测试资讯",
                    "摘要": "第一版摘要",
                    "内容": "第一版正文",
                    "类型": "科普类",
                    "项目名称": self.project.name,
                }
            ]
        )

        success_count, error_count = import_news_dataframe(first_data)

        self.assertEqual((success_count, error_count), (1, 0))
        imported = News.objects.get(title="导入测试资讯")
        self.assertEqual(imported.category, "science")
        self.assertEqual(imported.dance_project, self.project)
        self.assertEqual(imported.summary, "第一版摘要")

        updated_data = first_data.copy()
        updated_data.loc[0, "摘要"] = "更新后的摘要"
        updated_data.loc[0, "内容"] = "更新后的正文"

        success_count, error_count = import_news_dataframe(updated_data)

        self.assertEqual((success_count, error_count), (1, 0))
        self.assertEqual(News.objects.count(), 1)
        imported.refresh_from_db()
        self.assertEqual(imported.summary, "更新后的摘要")
        self.assertEqual(imported.content, "更新后的正文")

    def test_import_skips_rows_missing_title_or_content(self):
        invalid_data = pd.DataFrame(
            [
                {"标题": "", "内容": "有正文"},
                {"标题": "有标题", "内容": ""},
            ]
        )

        success_count, error_count = import_news_dataframe(invalid_data)

        self.assertEqual((success_count, error_count), (0, 2))
        self.assertFalse(News.objects.exists())

    def test_import_uses_alternate_column_when_primary_cell_is_nan(self):
        alternate_columns = pd.DataFrame(
            [
                {
                    "标题": "备用列资讯",
                    "内容": float("nan"),
                    "正文": "来自正文列的内容",
                    "类型": float("nan"),
                    "类别": "活动类",
                }
            ]
        )

        success_count, error_count = import_news_dataframe(alternate_columns)

        self.assertEqual((success_count, error_count), (1, 0))
        imported = News.objects.get(title="备用列资讯")
        self.assertEqual(imported.content, "来自正文列的内容")
        self.assertEqual(imported.category, "activity")
