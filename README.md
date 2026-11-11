# ai-tools-lab

用于直接调用 API 处理各类场景的方法测试项目。当前为脚手架阶段，已完成虚拟环境、依赖管理、环境变量管理与测试基础设施。

> 详细的项目解说（逐行代码、技术概念、参数含义、排错与扩展建议）见 [docs/PROJECT_GUIDE.md](docs/PROJECT_GUIDE.md)。

## 目录结构

```
.
├── main.py                  # 程序入口 / 冒烟测试
├── src/api_lab/config.py    # 环境变量读取与校验
├── tests/test_config.py     # 单元测试
├── requirements.txt         # 运行时依赖（固定版本）
├── requirements-dev.txt     # 开发依赖（含 pytest）
├── .env.example             # 环境变量模板
├── pytest.ini               # pytest 配置
└── docs/PROJECT_GUIDE.md    # 详细解说文档
```

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements-dev.txt

cp .env.example .env
# 编辑 .env，将 your_api_key_here 替换为真实 Key

python main.py
pytest -q
```

Windows 激活命令：

```powershell
.venv\Scripts\Activate.ps1
```

## 安全提示

- `.env` 保存真实密钥，**不要提交到 Git**。
- 仓库中只提交 `.env.example` 模板。
- 日志与终端输出不要打印完整 Key。

## 环境

- Python 3.14.4（如遇第三方 SDK 兼容问题，可改用 Python 3.12）
- `requests==2.34.2`
- `python-dotenv==1.2.4`
- `pytest==9.2.0`
