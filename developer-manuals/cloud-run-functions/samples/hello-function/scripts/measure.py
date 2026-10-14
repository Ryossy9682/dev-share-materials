"""少数の逐次リクエストで、実測応答時間と成功数をCSVに記録します。"""
import argparse
import csv
import json
from pathlib import Path
import subprocess
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request


def main():
    """指定URLを計測します。実行料金やコールドスタートの判定は行いません。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8080/?name=Developer")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--output", default="results/latency.csv")
    parser.add_argument("--cloud-auth", action="store_true", help="gcloudの開発用IDトークンを使う")
    args = parser.parse_args()
    url = urllib.parse.urlsplit(args.url)
    if not 1 <= args.count <= 1000:
        parser.error("countは1～1000です。")
    if url.username or url.password or not url.hostname:
        parser.error("資格情報を含まない有効なURLを指定してください。")
    if url.scheme != "https" and not (url.scheme == "http" and url.hostname in {"localhost", "127.0.0.1"}):
        parser.error("クラウドはHTTPS、ローカルはlocalhost/127.0.0.1のHTTPを使います。")
    if args.cloud_auth and url.scheme != "https":
        parser.error("クラウド認証にはHTTPSが必要です。")
    if args.cloud_auth and not url.hostname.endswith(".run.app"):
        parser.error("このサンプルのクラウド認証はCloud Runのrun.app URLを指定してください。")
    headers = {}
    if args.cloud_auth:
        executable = shutil.which("gcloud")
        if not executable:
            parser.error("Google Cloud CLIが見つかりません。")
        token = subprocess.check_output([executable, "auth", "print-identity-token"], text=True).strip()
        headers["Authorization"] = "Bearer " + token
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    successes = 0
    durations = []
    with output.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(["request_number", "status", "elapsed_seconds", "expected_result"])
        for i in range(args.count):
            status, correct = 0, False
            started = time.perf_counter()
            try:
                req = urllib.request.Request(args.url, headers=headers)
                with urllib.request.urlopen(req, timeout=60) as response:
                    status = response.status
                    payload = json.load(response)
                    correct = status == 200 and payload == {"message": "Hello, Developer!"}
            except urllib.error.HTTPError as error:
                status = error.code
            except (urllib.error.URLError, TimeoutError, ValueError):
                pass
            elapsed = time.perf_counter() - started
            durations.append(elapsed)
            successes += int(correct)
            writer.writerow([i + 1, status, round(elapsed, 6), correct])
    ordered = sorted(durations)
    import math
    p95 = ordered[math.ceil(0.95 * len(ordered)) - 1]
    print(f"successes={successes}/{args.count} mean={sum(durations)/len(durations):.6f}s p95={p95:.6f}s")
    print(f"CSV: {output}")
    print("これはクライアント側の応答時間です。課金時間・費用・初回起動の判定は別途確認してください。")
    if successes != args.count:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
