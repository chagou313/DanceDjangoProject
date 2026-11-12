# 非遗传统舞蹈平台

一个基于 Django 的中国非物质文化遗产传统舞蹈学习与交流平台，收录 356 个国家级非遗传统舞蹈项目及 379 位代表性传承人。

## 功能

| 模块 | 地址 | 说明 |
| --- | --- | --- |
| 新闻资讯 | `/news/` | 非遗活动、政策与项目导读 |
| 舞蹈起源 | `/origin/` | 非遗舞蹈项目与传承人资料，按地区浏览 |
| 知识图谱 | `/knowledge/` | 每个项目的动作模块、招式、知识点与学习资源；个性化推荐、学习路径、学习进度 |
| AI 智能问答 | `/knowledge/ai-chat/` | 基于通义千问的非遗舞蹈问答 |
| 答题闯关 | `/quiz/` | 分级关卡、计时答题、错题本 |
| 交流社区 | `/community/` | 发帖、评论、点赞、收藏、话题广场 |
| 个人主页 | `/profile/` | 个人资料与学习概况 |

## 快速开始

需要 Python 3.10 及以上版本。

**macOS：**在 Finder 中双击 `启动网站.command`。它会自动创建虚拟环境、安装依赖、执行迁移并启动网站，就绪后自动打开浏览器。第一次运行若提示“来自身份不明的开发者”，右键选择“打开”即可。

**命令行（macOS / Linux）：**

```bash
bash start.sh
```

**Windows：**

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

启动后访问 http://127.0.0.1:8000 。

## 数据与图片

为保护用户隐私，以下内容不在仓库中，需要单独拷贝到项目根目录：

- `db.sqlite3`：网站数据库（用户、知识图谱、题库、社区内容等）
- `media/`：用户上传与项目图片

没有数据库时，`start.sh` 会自动创建空数据库并生成新闻导读。舞蹈项目可从 `data/traditional_dance_data.xlsx` 导入，具体步骤见 `data/README.txt`；知识图谱与题库可用下面的命令生成示例数据：

```bash
python manage.py generate_all_real_knowledge_data
python manage.py generate_quiz_questions --limit 1000
python manage.py init_topics
```

## 配置

复制 `.env.example` 为 `.env`，按需填写。`.env` 不会被提交。

- `QWEN_API_KEY`：通义千问 API Key（[阿里云百炼](https://bailian.console.aliyun.com/)）。未配置时 AI 问答返回内置回复。
- 默认使用 SQLite。改用 MySQL：设置 `DB_ENGINE=mysql` 及 `DB_*` 各项，并执行 `pip install -r requirements-mysql.txt`。

## 常用管理命令

| 命令 | 作用 |
| --- | --- |
| `import_from_excel` / `import_all_data` | 从 Excel 导入舞蹈项目与传承人 |
| `restore_project_images` | 按项目 ID 恢复项目图片路径 |
| `seed_news --if-empty` | 根据舞蹈项目生成新闻导读 |
| `init_topics` | 初始化社区话题 |
| `check_duplicate_interactions` | 检查并清理重复的点赞、收藏记录 |
| `generate_all_real_knowledge_data` | 为舞蹈项目生成知识图谱示例数据 |
| `generate_quiz_questions` | 根据知识图谱生成答题题目 |

## 项目结构

```
DancedjangoProject/   项目设置与路由
dance/                首页、登录注册、个人主页
news/                 新闻资讯
origin/               舞蹈项目、传承人、地区
knowledge/            知识图谱、推荐、学习路径、AI 问答
quiz/                 答题闯关
community/            交流社区
templates/            页面模板
static/               站点静态图片
data/                 Excel 原始数据与导入说明
tests/                启动配置测试
```

## 测试

```bash
python manage.py test
```
