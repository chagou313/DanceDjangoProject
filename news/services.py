import math

from django.contrib.auth.models import User
from django.utils.html import escape, format_html, strip_tags
from django.utils.text import Truncator

from news.models import News
from origin.models import DanceProject


SYSTEM_AUTHOR_USERNAME = "platform_editor"


def get_system_author():
    """Return the inactive account used for locally generated platform content."""
    author, created = User.objects.get_or_create(
        username=SYSTEM_AUTHOR_USERNAME,
        defaults={"is_active": False},
    )
    if created:
        author.set_unusable_password()
        author.save(update_fields=["password"])
    return author


def _clean_text(value):
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return " ".join(str(value).split())


def _first_text(row, *column_names):
    for column_name in column_names:
        value = _clean_text(row.get(column_name))
        if value:
            return value
    return ""


def _project_guide_content(project):
    introduction = _clean_text(project.introduction)
    if not introduction:
        introduction = f"{project.name}是收录于本站的非物质文化遗产传统舞蹈项目。"

    return str(
        format_html(
            "<p>{}</p><p><strong>项目编号：</strong>{}</p>"
            "<p><strong>申报地区或单位：</strong>{}</p>"
            "<p>本文依据本站现有项目资料整理，供学习与检索使用。</p>",
            introduction,
            _clean_text(project.project_code) or "暂无",
            _clean_text(project.declare_region) or "暂无",
        )
    )


def seed_project_guides(limit=12, only_if_empty=False):
    """Create deterministic, non-fiction project guides in the active news table."""
    if only_if_empty and News.objects.exists():
        return 0, True

    author = get_system_author()
    projects = DanceProject.objects.order_by("project_code", "id")[: max(0, limit)]
    created_count = 0

    for index, project in enumerate(projects):
        introduction = _clean_text(strip_tags(project.introduction))
        summary = Truncator(introduction).chars(150) if introduction else (
            f"了解{project.name}的项目编号、申报地区与基本资料。"
        )
        _, created = News.objects.get_or_create(
            title=f"项目导读：{project.name}",
            defaults={
                "summary": summary,
                "content": _project_guide_content(project),
                "category": "science",
                "dance_project": project,
                "author": author,
                "is_hot": index < 6,
            },
        )
        created_count += int(created)

    return created_count, False


NEWS_CATEGORY_MAP = {
    "科普类": "science",
    "科普": "science",
    "science": "science",
    "活动类": "activity",
    "活动资讯": "activity",
    "activity": "activity",
    "政策类": "policy",
    "政策法规": "policy",
    "policy": "policy",
    "传承人类资讯": "inheritor",
    "传承人": "inheritor",
    "inheritor": "inheritor",
}


def import_news_dataframe(dataframe):
    """Import an Excel-shaped dataframe into the active news model."""
    author = get_system_author()
    success_count = 0
    error_count = 0

    for _, row in dataframe.iterrows():
        title = _first_text(row, "标题")
        content = _first_text(row, "内容", "正文")
        if not title or not content:
            error_count += 1
            continue

        category_label = _first_text(row, "类型", "类别")
        category = NEWS_CATEGORY_MAP.get(category_label, "science")
        project_name = _first_text(row, "项目名称", "关联项目", "舞蹈项目")
        project = None
        if project_name:
            project = DanceProject.objects.filter(name=project_name).first()
            if project is None:
                project = DanceProject.objects.filter(name__contains=project_name).first()

        summary = _first_text(row, "摘要", "简介")
        if not summary:
            summary = Truncator(strip_tags(content)).chars(150)

        News.objects.update_or_create(
            title=title,
            defaults={
                "summary": summary,
                "content": str(escape(content)),
                "category": category,
                "dance_project": project,
                "author": author,
            },
        )
        success_count += 1

    return success_count, error_count
