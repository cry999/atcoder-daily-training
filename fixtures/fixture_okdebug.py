# fixture: stdout は正解 (N → N*2) だが stderr に [DEBUG] を吐く (要件 044)。
#   通常実行 (submit 以外) → 判定は stdout のみ比較するので PASS。
#   --submit → サンプルは通過するが提出前チェックで [DEBUG] 出力を検出 → 確認。
#              非 TTY (run.sh) では自動で「いいえ」となり提出準備せず exit 1。
import sys

n = int(input())
print("[DEBUG] n =", n, file=sys.stderr)
print(n * 2)
