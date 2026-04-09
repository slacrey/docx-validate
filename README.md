# docx-validate

用于 `.docx` 文档检测服务的后端引导工程。当前版本已经提供：

- FastAPI 应用骨架和健康检查接口
- 基于 SQLAlchemy 的任务、规则集元数据持久化
- 文档上传、任务创建、任务状态查询
- 占位校验执行流，会生成空问题报告 `results/{task_no}/report.json`

## 环境要求

- Python 3.11+

## 首次安装

推荐使用项目根目录下的 `.venv` 虚拟环境：

```bash
make install
```

上面的命令会自动：

- 创建 `.venv`
- 安装项目和开发依赖

如果你想手动执行，等价命令是：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
```

## 运行测试

```bash
make test
```

## 本地启动

日常开发直接使用：

```bash
make run
```

`make run` 会强制使用项目内的 `.venv`，并自动设置 `PYTHONPATH=src`，适合当前 `src/` 布局。

如果你想手动启动，等价命令是：

默认会在当前目录创建 `docx_validate.db` 和 `var/storage/`。也可以通过环境变量覆盖：

- `DOCX_VALIDATE_DATABASE_URL`
- `DOCX_VALIDATE_STORAGE_ROOT`
- `DOCX_VALIDATE_API_PREFIX`

启动命令：

```bash
PYTHONPATH=src .venv/bin/python -m uvicorn docx_validate.main:app --host 127.0.0.1 --port 8000 --reload
```

## 当前接口

- `GET /api/v1/health`
- `POST /api/v1/rules`
- `GET /api/v1/rules/{id}`
- `POST /api/v1/tasks`
- `GET /api/v1/tasks/{task_no}`

## 后续迭代方向

- 模板元数据和模板上传接口
- 真实校验引擎与异步任务执行
- JSON/CSV 报告与批注文档产出
