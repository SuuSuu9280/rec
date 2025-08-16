import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# ===== 設定 =====
URL_LIST_FILE = "urls.txt"      # URLリスト（1行に1URL）
OUTPUT_DIR = "url_contents"     # 出力ディレクトリ

# 出力ディレクトリがなければ作成
os.makedirs(OUTPUT_DIR, exist_ok=True)

# URLリスト読み込み
with open(URL_LIST_FILE, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

unreadable_urls = []

for url in urls:
    print(f"処理中: {url}")
    try:
        # ページ取得
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # HTMLを解析して本文抽出
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)

        # URLからファイル名を生成（スラッシュや特殊文字は置換）
        parsed = urlparse(url)
        safe_name = parsed.netloc.replace(".", "_") + parsed.path.replace("/", "_")
        if not safe_name:  # パスが空の場合
            safe_name = parsed.netloc.replace(".", "_")
        file_path = os.path.join(OUTPUT_DIR, f"{safe_name}.txt")

        # ファイルに保存
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"URL: {url}\n\n{text}")

    except Exception as e:
        print(f"読み込み失敗: {url} → {e}")
        unreadable_urls.append(url)

# 読み込めなかったURL報告
if unreadable_urls:
    print("\n--- 読み込めなかったURL ---")
    for u in unreadable_urls:
        print(u)
else:
    print("\nすべてのURLを処理できました。")
