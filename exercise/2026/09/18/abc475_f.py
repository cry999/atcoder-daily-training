# >>> atcoder-stat >>>
# started_at  = 2026-09-18T11:06:48+09:00
# solved_at   = 2026-09-18T11:22:43+09:00
# duration_ms = 955458
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<
import sys

input = sys.stdin.readline


H, W = map(int, input().split())

if H > W:
    H, W = W, H
    is_white = [[False] * W for _ in range(H)]
    for w in range(W):
        s = input().strip()
        for h in range(H):
            is_white[h][w] = s[h] == "."
else:
    is_white = [[s == "." for s in input().strip()] for _ in range(H)]


# white_cols
white_cols = [False] * W

# prefix[i] := 0 ~ i-1 列目までの白の列の数
prefix = [0] * (W + 1)

ans = 1
for top in range(H):
    for w in range(W):
        white_cols[w] = is_white[top][w]

    for bottom in range(top, H):
        for w in range(W):
            white_cols[w] |= is_white[bottom][w]

        # top, bottom の行に最後に出現した白の列
        last_top, last_bottom = -1, -1
        prefix[0] = 0

        for right in range(W):
            if is_white[top][right]:
                last_top = right

            if is_white[bottom][right]:
                last_bottom = right

            # 白のある列をカウント
            prefix[right + 1] = prefix[right] + white_cols[right]
            if not white_cols[right]:
                # この列に白がない場合は、前提条件を満たさない。
                continue

            # top, bottom, right, left 全てに白がある長方形をカウントアップ
            # top, bottom, right は今の位置に固定して、left について累積和で考える
            left = min(last_top, last_bottom)
            ans += prefix[left + 1]

print(ans)
