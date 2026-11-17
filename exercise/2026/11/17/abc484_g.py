# >>> atcoder-stat >>>
# started_at  = 2026-11-17T09:43:37+09:00
# solved_at   = 2026-11-17T10:24:47+09:00
# duration_ms = 2470695
# ac          = true
# editorial   = true
# knowledge   = 1
# translation = 1
# complexity  = 1
# impl        = 1
# verify      = 1
# <<< atcoder-stat <<<
S = input()
X = input()
Y = input()

LS = len(S)
LX, LY = len(X), len(Y)

MOD = 998244353

# 各文字をおける位置の bitmask
ok_x = [0, 0]
for i, c in enumerate(X):
    for b in range(2):
        if c == "?" or c == str(b):
            ok_x[b] |= 1 << i

ok_y = [0, 0]
for i, c in enumerate(Y):
    for b in range(2):
        if c == "?" or c == str(b):
            ok_y[b] |= 1 << i

# X, Y が完成していることを表す bit
end_x = 1 << (LX - 1)
end_y = 1 << (LY - 1)

# dp[(mx, my)] = その状態になる文字数
dp = {(end_x, 0): 1}

for s in S:
    ndp: dict[tuple[int, int], int] = {}

    for (mx, my), v in dp.items():
        for c in range(2):
            if s != "?" and s != str(c):
                # おけない
                continue

            nx = (mx << 1) & ok_x[c]
            ny = (my << 1) & ok_y[c]

            if (mx & end_x or my & end_y) and (ok_x[c] & 1):
                nx |= 1

            if (mx & end_x) and (ok_y[c] & 1):
                ny |= 1

            if nx or ny:
                k = (nx, ny)
                ndp[k] = (ndp.get(k, 0) + v) % MOD

    dp = ndp

ans = sum(v for (mx, my), v in dp.items() if mx & end_x or my & end_y) % MOD
print(ans)
