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
