# fixture: 簡易インタラクティブ。
#   1 行目で N を読む → "QUERY i" を i=1..N で順に print → 都度応答を読む → 最後に "DONE" を print。
# PYTHONUNBUFFERED=1 が runner で自動セットされるので明示的な flush は不要。
n = int(input())
for i in range(1, n + 1):
    print(f"QUERY {i}")
    _ = input()  # 応答を読み捨てる
print("DONE")
