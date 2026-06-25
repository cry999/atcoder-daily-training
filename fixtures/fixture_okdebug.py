# fixture: stdout は正解 (N → N*2) だが stderr に [DEBUG] を吐く (要件 044 / 049)。
#   通常実行 (submit 以外) → 判定は stdout のみ比較するので PASS。
#   --submit → 提出前チェックはコメントアウト後ソースを実行する (要件 049) が、この
#              [DEBUG] 出力は print(...) ではなく sys.stderr.write なので debugstrip の
#              regex に拾われず生き残る = コメントアウト漏れ。実行時に検出され確認 →
#              非 TTY (run.sh) では自動で「いいえ」となり提出準備せず exit 1。
import sys

n = int(input())
sys.stderr.write(f"[DEBUG] n = {n}\n")
print(n * 2)
