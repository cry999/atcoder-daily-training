# fixture: valid JSON ペイロードの [DEBUG] 行を 1 本吐く (要件 047 pp 用)。
#   -d 無し       → [DEBUG] 行が出力に混ざり FAIL
#   -d 付き       → [DEBUG] 行がフィルタされて PASS (出力 10)
#   -d --pp 付き  → debug: セクションで JSON が 2-space インデント整形される
# json.dumps で 1 行 JSON を吐くのが pp の推奨パターン (利用手引参照)。
import json

n = int(input())
print("[DEBUG] " + json.dumps({"grid": [[0, 1], [2, 3]], "n": n}))
print(n * 2)
