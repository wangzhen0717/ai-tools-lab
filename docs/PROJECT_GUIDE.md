# 项目解说文档

本文档面向第一次接触本项目的读者，目标是把“这个项目怎么跑起来、每行代码在做什么、涉及哪些概念、参数是什么意思”讲清楚。内容与当前代码一一对应，代码位置用 `文件:行号` 标注。

---

## 1. 项目总览

### 1.1 项目定位

这是一个用于**直接调用 API 处理各类场景**的实验型项目。当前处于脚手架阶段：完成虚拟环境、依赖管理、环境变量管理和测试基础设施，还没有发起真实的 API 请求。

### 1.2 一次运行发生了什么

```
Shell 环境变量 / .env 文件
        │
        │  load_dotenv() 读取 .env
        ▼
   os.environ（进程环境变量，键值都是字符串）
        │
        │  os.getenv("ZHIPU_API_KEY")
        ▼
   get_zhipu_api_key()
        │
        │  返回 str 或 None
        ▼
   main.py：None → 提示配置；有值 → 打印长度
```

关键点：`.env` 文件**不会自动生效**，必须由代码显式调用 `load_dotenv()`（或由外部工具注入环境变量），之后 `os.getenv` 才能读到。

### 1.3 目录结构

```
ai-tools-lab/
├── .venv/                     # 虚拟环境，不应提交到 Git
├── .env                       # 本地真实密钥，空文件，不提交
├── .env.example               # 配置模板，提交到 Git
├── .gitignore                 # Git 忽略规则
├── requirements.txt           # 运行时依赖（固定版本）
├── requirements-dev.txt       # 开发依赖（含 pytest）
├── pytest.ini                 # pytest 配置
├── main.py                    # 程序入口 / 冒烟测试
├── README.md                  # 快速开始
├── docs/
│   └── PROJECT_GUIDE.md       # 本文档
├── src/
│   └── api_lab/
│       ├── __init__.py        # 标记 api_lab 为 Python 包
│       └── config.py          # 配置与环境变量读取
└── tests/
    └── test_config.py         # 配置读取的单元测试
```

---

## 2. 逐文件逐行讲解

### 2.1 `main.py`（程序入口）

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from api_lab.config import get_zhipu_api_key


def main() -> None:
    api_key = get_zhipu_api_key()

    if api_key is None:
        print("未读取到 ZHIPU_API_KEY：请复制 .env.example 为 .env 并填入真实 Key。")
        return

    print(f"已读取到 ZHIPU_API_KEY（长度 {len(api_key)}），环境变量读取正常。")
    print("下一步可在此接入 requests 调用智谱 API。")


if __name__ == "__main__":
    main()
```

| 位置 | 说明 |
| --- | --- |
| `main.py:1-2` | 导入标准库 `sys`（运行时环境）和 `pathlib.Path`（跨平台路径操作）。 |
| `main.py:4` | `__file__` 是当前文件路径；`.resolve()` 转成绝对路径并解析符号链接；`.parent` 得到项目根目录；`/ "src"` 拼接出 `src` 目录。`sys.path.insert(0, ...)` 把它放到模块搜索路径**最前面**，因此 `import api_lab` 能找到 `src/api_lab`。这是 src layout 下不安装包也能直接运行的做法。 |
| `main.py:6` | 从 `api_lab.config` 模块导入函数。注意这行必须放在修改 `sys.path` 之后，否则会 `ModuleNotFoundError`。 |
| `main.py:9` | 定义入口函数，`-> None` 表示不返回任何值。 |
| `main.py:10` | 读取 Key。返回值只有两种情况：非空字符串或 `None`。 |
| `main.py:12-14` | 没有 Key 时打印提示并提前 `return`，避免后续逻辑在无凭据下运行。 |
| `main.py:16` | **只打印 Key 的长度，不打印 Key 本身**，避免密钥出现在终端、日志或录屏中。 |
| `main.py:20-21` | Python 的模块保护：直接运行 `python main.py` 时，`__name__` 等于 `"__main__"`，于是执行 `main()`；被其他文件 `import main` 时不会自动执行，避免副作用。 |

**参数含义**

- `sys.path`：Python 查找模块的目录列表。`sys.path[0]` 优先级最高。
- `Path(__file__).resolve().parent`：当前脚本所在目录（本项目根目录）。
- `insert(0, ...)`：插到列表第 0 位，而不是追加到末尾。

### 2.2 `src/api_lab/config.py`（配置读取）

```python
import os

from dotenv import load_dotenv

PLACEHOLDER_API_KEY = "your_api_key_here"


def load_env() -> None:
    load_dotenv()


def get_zhipu_api_key() -> str | None:
    load_dotenv()

    api_key = os.getenv("ZHIPU_API_KEY")
    if api_key is None:
        return None

    api_key = api_key.strip()
    if not api_key or api_key == PLACEHOLDER_API_KEY:
        return None

    return api_key
```

| 位置 | 说明 |
| --- | --- |
| `config.py:1` | `os` 提供环境变量访问能力。 |
| `config.py:3` | 从第三方库 `python-dotenv` 导入 `load_dotenv`，用来把 `.env` 文件内容注入 `os.environ`。 |
| `config.py:5` | 占位符常量。`.env.example` 里的值就是它，用于识别“用户还没填真实 Key”。 |
| `config.py:8-9` | 公开的加载函数。调用 `load_dotenv()` 后，后续代码才能用 `os.getenv` 读到 `.env` 里的值。 |
| `config.py:12` | 返回类型 `str | None` 是 Python 3.10+ 的联合类型写法，等价于 `Optional[str]`：要么字符串，要么 `None`。 |
| `config.py:13` | 每次读取都确保 `.env` 已加载。`load_dotenv()` 是幂等且默认不覆盖已有变量的，重复调用安全。 |
| `config.py:15` | `os.getenv` 在键不存在时返回 `None`（而不是抛异常）。 |
| `config.py:16-17` | 键完全不存在，直接返回 `None`。 |
| `config.py:19` | `strip()` 去掉首尾空白，防止用户填了空格导致“看起来有值实际无效”。 |
| `config.py:20-21` | 空字符串、纯空白、或仍是占位符 `your_api_key_here`，都视为未配置。 |
| `config.py:23` | 返回清洗后的真实 Key。 |

**为什么不在 main.py 里直接写 `load_dotenv()`？**

集中到 `config.py` 后，未来新增 `zhipu.py`、脚本、测试都能复用同一套读取规则，避免每个入口各写一遍、规则不一致。

### 2.3 `tests/test_config.py`（单元测试）

```python
import pytest

from api_lab.config import get_zhipu_api_key


@pytest.fixture(autouse=True)
def disable_dotenv(monkeypatch):
    monkeypatch.setattr("api_lab.config.load_dotenv", lambda: None)


def test_get_api_key_from_env(monkeypatch):
    monkeypatch.setenv("ZHIPU_API_KEY", "test_key_123")

    assert get_zhipu_api_key() == "test_key_123"
```

四个用例分别验证：

| 用例 | 目的 |
| --- | --- |
| `test_get_api_key_from_env` | 设置了环境变量时，能正确读回。 |
| `test_missing_api_key` | 变量不存在时返回 `None`。 |
| `test_placeholder_api_key_is_ignored` | 值仍是 `your_api_key_here` 时视为未配置。 |
| `test_blank_api_key_is_ignored` | 值为纯空白时视为未配置。 |

**参数与 fixture 含义**

- `monkeypatch`：pytest 内置 fixture，提供 `setenv` / `delenv` / `chdir` / `setattr` 等能力，**测试结束后自动恢复原状**，不会污染其他用例。
- `@pytest.fixture(autouse=True)`：定义一个自动生效的 fixture，每个用例都会执行，无需在参数里显式声明。
- `monkeypatch.setattr("api_lab.config.load_dotenv", lambda: None)`：把 `config.py` 里导入的 `load_dotenv` 临时替换成空函数。这样测试**只依赖用例自己设置的环境变量**，不会读取本地 `.env` 里的真实 Key。
- `monkeypatch.setenv` / `delenv`：设置或删除环境变量，用例结束自动回滚。
- `assert`：pytest 会重写断言，失败时打印两边的实际值，便于定位。
- 测试函数名必须以 `test_` 开头，pytest 才会自动发现。

> **为什么要屏蔽 `load_dotenv`**
> `python-dotenv` 默认从**调用 `load_dotenv()` 的文件所在目录**开始向上查找 `.env`。这里的调用方是 `src/api_lab/config.py`，因此即使把工作目录切到临时目录，仍会向上找到项目根目录的 `.env`。
> 早期测试使用 `monkeypatch.chdir(tmp_path)` 试图隔离，但当 `.env` 填入真实 Key 后，`test_missing_api_key` 会读到真实 Key 而失败，并且失败信息可能把 Key 打印到终端。
> 现在通过 autouse fixture 将 `load_dotenv` 替换为空操作，测试不再依赖也不触碰本地密钥，稳定且安全。
> 其他可选方案：让 `get_zhipu_api_key(dotenv_path: str | None = None)` 支持显式传入路径，或使用 `pytest-env` 等插件隔离配置。

### 2.4 `pytest.ini`

```ini
[pytest]
pythonpath = src
testpaths = tests
```

- `[pytest]`：pytest 配置节。
- `pythonpath = src`：pytest 启动时把 `src` 加入 `sys.path`，测试里才能直接 `import api_lab`，无需安装包或手写 `sys.path`。
- `testpaths = tests`：只在 `tests/` 目录下收集用例，运行更快，避免误扫 `.venv`。

### 2.5 `requirements.txt` 与 `requirements-dev.txt`

```text
# requirements.txt
requests==2.34.2
python-dotenv==1.2.4
```

```text
# requirements-dev.txt
-r requirements.txt
pytest==9.2.0
```

- `==`：**精确锁定版本**，保证不同机器、不同时间安装到完全一致的版本，避免“昨天能跑今天不行”。
- `-r requirements.txt`：把运行时依赖文件包含进来，开发依赖只写增量，避免重复维护。
- 传递依赖（`certifi`、`charset-normalizer`、`idna`、`urllib3`、`pluggy` 等）由 pip 根据上述包自动解析，当前没有逐个锁死。若需要完全可复现的锁文件，可以后续引入 `pip freeze > requirements.lock`、`pip-tools` 或 `uv lock`。

### 2.6 `.gitignore`

```gitignore
.venv/
venv/
__pycache__/
*.py[cod]
*$py.class
*.so
.env
.env.*
!.env.example
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
htmlcov/
build/
dist/
*.egg-info/
.idea/
.vscode/
.DS_Store
```

| 规则 | 作用 |
| --- | --- |
| `.venv/`、`venv/` | 虚拟环境体积大且与机器相关，不入库。 |
| `__pycache__/`、`*.py[cod]` | Python 字节码缓存，可随时重建。`[cod]` 匹配 `.pyc`、`.pyo`、`.pyd`。 |
| `*.so` | 编译生成的动态库。 |
| `.env` | 真实密钥，绝对不能提交。 |
| `.env.*` | 忽略 `.env.local`、`.env.production` 等变体。 |
| `!.env.example` | `!` 表示反向包含，让模板文件仍能被提交。规则顺序很重要：先忽略、再排除。 |
| `.pytest_cache/`、`.ruff_cache/`、`.mypy_cache/` | 各类工具缓存。 |
| `.coverage`、`htmlcov/` | 覆盖率产物。 |
| `build/`、`dist/`、`*.egg-info/` | 打包产物。 |
| `.idea/`、`.vscode/`、`.DS_Store` | 编辑器与操作系统生成的本地文件。 |

### 2.7 `.env` 与 `.env.example`

- `.env`：本地真实配置，当前是空文件，已被 `.gitignore` 忽略。
- `.env.example`：提交到仓库的模板，内容为 `ZHIPU_API_KEY=your_api_key_here`，告诉协作者需要哪些变量、格式是什么。

标准做法：新成员克隆仓库后执行 `cp .env.example .env`，再把占位符替换成自己的真实 Key。

---

## 3. 技术概念详解

### 3.1 虚拟环境（`.venv`）

**它是什么**：一个独立的 Python 运行环境目录，拥有自己的解释器入口、`pip` 和 `site-packages`。本项目创建在 `.venv/`。

**为什么需要**：不同项目可能依赖同一个库的不同版本。全局安装会互相冲突；虚拟环境让每个项目“各用各的”。

**创建命令**

```bash
python3 -m venv .venv
```

- `-m venv`：运行标准库 `venv` 模块。
- 生成 `pyvenv.cfg`、`bin/`（Windows 是 `Scripts/`）、`lib/python3.14/site-packages/`。
- 默认不继承系统已安装的第三方包。

**激活做了什么**

```bash
source .venv/bin/activate
```

激活脚本主要修改当前 Shell 的 `PATH`，把 `.venv/bin` 放到最前面。于是：

- `python` → `.venv/bin/python`
- `pip` → `.venv/bin/pip`
- 新安装的包 → `.venv/lib/python3.14/site-packages`

激活只影响**当前终端会话**，关闭终端或执行 `deactivate` 即失效。

**为什么不激活也能用**：本文档中的命令使用 `.venv/bin/python -m pytest` 这类绝对路径，效果等价，且不依赖 Shell 状态。

### 3.2 pip 与依赖版本管理

- `pip` 是 Python 包安装器。
- `python -m pip` 比直接写 `pip` 更可靠：明确使用当前解释器对应的 pip，避免 PATH 指向错误的 pip。
- `pip install --upgrade pip`：先升级安装器自身，减少解析旧版本依赖时的兼容问题。
- `pip install -r requirements-dev.txt`：按文件批量安装。
- `pip freeze`：输出当前环境里**所有已安装包及其精确版本**，可用于核对或生成锁文件。
- 版本约束符：
  - `==1.2.3` 精确等于；
  - `>=1.2,<2` 范围；
  - `~=1.2` 兼容版本（不低于 1.2，不跨大版本）。
  本项目对直接依赖使用 `==`，追求可复现。

### 3.3 环境变量

**它是什么**：操作系统提供给进程的键值对，常用于存放密钥、开关、路径等“因环境而异”的配置。值**永远是字符串**。

```python
os.getenv("ZHIPU_API_KEY")        # 不存在返回 None
os.getenv("PORT", "8000")         # 不存在返回默认值 "8000"
os.environ["ZHIPU_API_KEY"]       # 不存在抛 KeyError
```

**优先级**（本项目）：

1. Shell 中已存在的环境变量；
2. `.env` 文件中的值；
3. 代码中的默认值 / 占位符判断。

原因：`load_dotenv()` 默认 `override=False`，**不会覆盖已存在的环境变量**。所以 CI 或生产环境用真实环境变量注入时，会覆盖本地 `.env`，这是期望行为。

### 3.4 python-dotenv 与 `load_dotenv()`

- 作用：解析 `.env` 文件（`KEY=VALUE` 每行一条），写入 `os.environ`。
- 默认查找规则：从调用方文件所在目录开始，逐级向上查找 `.env`，直到文件系统根目录。
- 默认 `override=False`：已存在的键不覆盖。
- 支持变量引用，例如 `BASE_URL=https://example.com`、`API_URL=${BASE_URL}/v1`。
- 它**只负责加载**，不负责校验；校验逻辑由 `config.py` 自己完成。

常见误区：只写了 `.env` 但没有调用 `load_dotenv()`，`os.getenv` 依然读不到。

### 3.5 src layout 与包导入

```
src/
└── api_lab/
    ├── __init__.py
    └── config.py
```

- `src/` 是“源码根目录”，包放在其下。
- `__init__.py` 让 `api_lab` 成为常规包（Python 3 的命名空间包可以没有它，但显式保留更清晰）。
- 导入路径：`api_lab.config` 对应 `src/api_lab/config.py`。
- 两种让 Python 找到包的方式：
  1. 运行时把 `src` 加入 `sys.path`（`main.py:4` 的做法）；
  2. 测试时由 `pytest.ini` 的 `pythonpath = src` 注入。

**src layout 的好处**：避免把项目根目录误当成包目录，减少“本地同名文件遮蔽已安装库”的问题，也让“源码”和“项目配置”边界清晰。

### 3.6 类型注解

```python
def main() -> None: ...
def get_zhipu_api_key() -> str | None: ...
```

- `-> None`：函数不返回值。
- `str | None`：PEP 604 联合类型，Python 3.10+ 支持。
- 注解**不强制运行时检查**，主要提升可读性、编辑器补全和静态检查（如 mypy）能力。

### 3.7 pytest 基础

- **自动发现**：默认收集 `test_*.py` 或 `*_test.py` 中的 `test_*` 函数/方法。
- **断言**：直接写 `assert 实际 == 期望`，失败时 pytest 会展示详细差异。
- **fixture**：测试依赖的“准备/清理”机制。用例参数名与 fixture 同名即可注入。
  - `monkeypatch`：临时修改环境变量、属性、工作目录，用例结束自动回滚。
  - `tmp_path`：每个用例独享的临时目录。
- **隔离原则**：用例之间不应共享可变状态；不要依赖执行顺序。
- 常用命令：
  - `pytest -q`：安静模式，只显示结果；
  - `pytest -v`：显示每个用例名字；
  - `pytest tests/test_config.py::test_missing_api_key`：只跑单个用例；
  - `pytest -k "api_key"`：按名字关键字筛选。

### 3.8 Python 3.14 说明

本项目当前使用 Python 3.14.4。`requests`、`python-dotenv`、`pytest` 工作正常。

需要注意：3.14 较新，未来若接入智谱官方 SDK 或其他依赖 C 扩展 / Pydantic 的库，可能遇到暂未提供 wheel 或兼容性问题。遇到安装失败时，优先考虑改用 Python 3.12 创建虚拟环境。

---

## 4. 参数与配置速查表

| 名称 | 位置 | 含义 | 当前值 |
| --- | --- | --- | --- |
| `ZHIPU_API_KEY` | 环境变量 / `.env` | 智谱 API 的访问密钥 | 空（待填写） |
| `PLACEHOLDER_API_KEY` | `config.py:5` | 占位符识别值，出现即视为未配置 | `your_api_key_here` |
| `override` | `load_dotenv()` 参数 | 是否用 `.env` 覆盖已有环境变量 | 默认 `False` |
| `pythonpath` | `pytest.ini` | pytest 额外加入的模块搜索路径 | `src` |
| `testpaths` | `pytest.ini` | pytest 收集用例的目录 | `tests` |
| `.venv/` | 项目根目录 | 虚拟环境目录 | 已创建 |
| `requests==2.34.2` | `requirements.txt` | HTTP 客户端库，后续调用 API 使用 | 已锁定 |
| `python-dotenv==1.2.4` | `requirements.txt` | `.env` 加载库 | 已锁定 |
| `pytest==9.2.0` | `requirements-dev.txt` | 测试框架 | 已锁定 |

### 后续调用 API 时常见参数（预告）

真正写 `src/api_lab/zhipu.py` 时会用到：

- `timeout`：请求超时时间（秒），**必须设置**，否则异常时可能长时间挂起。
- `headers={"Authorization": f"Bearer {api_key}"}`：携带鉴权信息。
- `raise_for_status()`：对 4xx/5xx 抛异常，便于统一处理。
- `max_tokens` / `temperature` 等模型参数：控制输出长度与随机性。
- 重试策略：对 `429`（限流）、`5xx`（服务端错误）做指数退避。

---

## 5. 运行手册

### 5.1 Linux / macOS

```bash
cd /home/ubuntu/code/ai-tools-lab

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements-dev.txt

cp .env.example .env
# 编辑 .env，把 your_api_key_here 换成真实 Key

python main.py
pytest -q
```

### 5.2 Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1        # PowerShell
rem 或：.venv\Scripts\activate.bat  # CMD

python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python main.py
pytest -q
```

### 5.3 命令逐条解释

| 命令 | 解释 |
| --- | --- |
| `python3 -m venv .venv` | 创建虚拟环境。 |
| `source .venv/bin/activate` | 激活虚拟环境（Windows 用脚本路径）。 |
| `python -m pip install --upgrade pip` | 用虚拟环境内的 Python 升级 pip。 |
| `pip install -r requirements-dev.txt` | 安装运行时 + 开发依赖。 |
| `cp .env.example .env` | 由模板生成本地配置文件（已存在则跳过，直接编辑）。 |
| `python main.py` | 运行入口脚本。 |
| `pytest -q` | 运行全部测试，安静输出。 |
| `deactivate` | 退出虚拟环境。 |

### 5.4 预期输出

未配置 Key：

```
未读取到 ZHIPU_API_KEY：请复制 .env.example 为 .env 并填入真实 Key。
```

已配置 Key：

```
已读取到 ZHIPU_API_KEY（长度 32），环境变量读取正常。
下一步可在此接入 requests 调用智谱 API。
```

测试：

```
....                                                                     [100%]
4 passed in 0.04s
```

---

## 6. 常见问题排查

| 现象 | 可能原因 | 解决 |
| --- | --- | --- |
| 提示未读取到 Key | `.env` 为空 / 仍是占位符 / 未调用 `load_dotenv()` | 填入真实值；确认代码经过 `config.py` |
| 改了 `.env` 不生效 | Shell 里已有同名环境变量，`override=False` 不覆盖 | 用 `unset ZHIPU_API_KEY` 或检查 CI 注入 |
| `ModuleNotFoundError: api_lab` | 未激活虚拟环境 / 未按 src layout 注入路径 | 激活 `.venv`；直接运行 `main.py`；pytest 用 `pytest.ini` |
| `pytest: command not found` | 虚拟环境未激活或未安装开发依赖 | `pip install -r requirements-dev.txt` |
| 激活脚本无权限（Windows） | PowerShell 执行策略限制 | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `.env` 出现在 `git status` | `.gitignore` 未生效或被强制添加 | 确认规则；已跟踪则 `git rm --cached .env` |
| 测试读到了 `.env` 中的真实 Key | 测试未屏蔽 `load_dotenv`，它会从 `config.py` 向上找到项目 `.env` | 保留 2.3 节的 autouse fixture，或显式传入 `dotenv_path` |
| 安装依赖报编译错误 | Python 版本过新，依赖暂无 wheel | 改用 Python 3.12 重建虚拟环境 |

---

## 7. 后续扩展路线

### 7.1 新增 API 客户端

建议新增 `src/api_lab/zhipu.py`，职责单一：拼请求、发请求、解析响应。示例结构：

```python
import requests

from api_lab.config import get_zhipu_api_key

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"


def chat(prompt: str, timeout: float = 30.0) -> dict:
    api_key = get_zhipu_api_key()
    if api_key is None:
        raise RuntimeError("ZHIPU_API_KEY 未配置")

    response = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": "glm-4-flash", "messages": [{"role": "user", "content": prompt}]},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
```

具体 URL 与模型名以智谱官方文档为准。

### 7.2 测试策略

- 用 `respx` 或 `responses` mock HTTP，大部分用例不发真实请求；
- 真实调用用 `@pytest.mark.live` 标记，默认跳过：`pytest -m "not live"`；
- 对错误分支单独测试：超时、401、429、5xx、非法 JSON。

### 7.3 工程化增强

- 引入 `pyproject.toml`，统一项目元数据、工具配置；
- `ruff` 做 lint + format，`mypy` 做类型检查；
- `pre-commit` 钩子 + `gitleaks` 防止密钥误提交；
- `Makefile` 或 `justfile` 固化常用命令；
- 使用 `uv` 管理依赖与锁文件，速度更快、可复现性更强。

---

## 8. 安全检查清单

- [ ] `.env` 已在 `.gitignore` 中，且未被 Git 跟踪
- [ ] 仓库中只保留 `.env.example`，不含真实密钥
- [ ] 日志、异常、调试输出不打印完整 Key
- [ ] 密钥泄露后立即在服务商控制台轮换
- [ ] CI/CD 使用平台密钥管理，不把 `.env` 打包进镜像
- [ ] 提交前执行 `git diff --cached` 自查
- [ ] 为 API 调用设置超时与重试上限，避免费用与资源失控
