# >>> atcoder-stat >>>
# started_at  = 2026-09-16T00:34:20+09:00
# solved_at   = 2026-09-16T00:58:12+09:00
# duration_ms = 1432289
# ac          = true
# editorial   = true
# knowledge   = 2
# translation = 1
# complexity  = 2
# impl        = 1
# verify      = 2
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


H, W = map(int, input().split())
S = [list(input().strip()) for _ in range(H)]


if H > W:
    # H を短い方にしたいので H, W を入れ替える
    is_white = [[S[h][w] == "." for h in range(H)] for w in range(W)]
    H, W = W, H
else:
    is_white = [[S[h][w] == "." for w in range(W)] for h in range(H)]


ans = 1
prefix = [0] * (W + 1)
# has_white[c] := (c, u), (c, u+1), ..., (c, d) に白ますが存在するか?
has_white = [False] * W
for top in range(H):
    for c in range(W):
        has_white[c] = is_white[top][c]

    for bottom in range(top, H):
        # 新しく追加する行 d の白ますチェック
        for c in range(W):
            has_white[c] |= is_white[bottom][c]

        # top, bottom 行に最後に確認された白ますが存在する列
        last_top, last_bottom = -1, -1
        # 今見ている列よりも左側で白ますが存在する列を管理する
        left_cnt = 0

        prefix[0] = 0

        for right in range(W):
            if is_white[top][right]:
                last_top = right

            if is_white[bottom][right]:
                last_bottom = right

            prefix[right + 1] = prefix[right] + has_white[right]

            if not has_white[right]:
                continue

            limit = min(last_top, last_bottom)
            ans += prefix[limit + 1]

print(ans)
