# fixture: [DEBUG] 行を常に吐く。
#   -d 無し → 出力に [DEBUG] が混ざるため FAIL
#   -d 付き → [DEBUG] 行がフィルタされて PASS
# 実コードでは os.environ.get("DEBUG") で条件分岐するのが推奨パターン (利用手引参照)。
n = int(input())
print("[DEBUG] got n =", n)
result = n * 2
print("[DEBUG] computed result =", result)
print(result)
