# Django 项目一键启动设计

## 目标

让开发者在 macOS 或常见 Linux 环境中进入项目目录后，只运行 `./start.sh` 即可启动项目，无需预先安装或配置 MySQL。

## 方案

项目默认使用仓库内的 SQLite 数据库。启动脚本负责创建本地 Python 虚拟环境、安装运行依赖、执行数据库迁移，并启动 Django 开发服务器。

保留可选的 MySQL 配置入口：设置 `DB_ENGINE=mysql` 后，Django 从环境变量读取数据库名称、用户、密码、主机和端口。MySQL 驱动作为可选依赖，不影响默认 SQLite 启动。

## 文件与职责

- `start.sh`：定位项目目录、创建 `.venv`、安装 `requirements.txt`、执行迁移、启动开发服务器。
- `requirements.txt`：声明 SQLite 模式所需的 Django、Pillow 和 requests 依赖。
- `requirements-mysql.txt`：声明可选 MySQL 驱动并复用基础依赖。
- `DancedjangoProject/settings.py`：默认使用 SQLite；仅在明确指定 MySQL 时读取 MySQL 环境变量。
- `tests/test_startup_config.py`：验证默认数据库、MySQL 环境变量映射和启动文件约定。

## 启动接口

默认命令：

```bash
./start.sh
```

默认监听 `127.0.0.1:8000`。用户可设置 `HOST` 和 `PORT` 覆盖监听地址，例如：

```bash
HOST=0.0.0.0 PORT=8080 ./start.sh
```

## 数据与安全

SQLite 使用项目已有的 `db.sqlite3`，启动时执行迁移以补齐缺失表，不删除已有数据。

MySQL 密码不再写死在配置中。MySQL 模式使用 `DB_NAME`、`DB_USER`、`DB_PASSWORD`、`DB_HOST` 和 `DB_PORT`。现有第三方 API Key 不属于本次一键启动改动范围，但应后续迁移到环境变量并轮换。

## 错误处理

启动脚本使用严格错误模式；虚拟环境创建、依赖安装或迁移任一步失败时立即退出并保留原始错误信息。找不到 `python3` 时输出明确提示。

## 验证

1. 先编写配置测试并确认其在实现前失败。
2. 实现最小变更，使配置测试通过。
3. 执行 Django 自检和项目测试。
4. 使用 `./start.sh` 启动服务，确认首页及主要页面返回成功状态。

## 非目标

- 不引入 Docker。
- 不生成生产部署配置。
- 不自动创建或修改 MySQL 用户与数据库。
- 不重构现有业务模块。
