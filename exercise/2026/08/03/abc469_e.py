# >>> atcoder-stat >>>
# started_at  = 2026-08-03T15:20:00+09:00
# solved_at   = 2026-08-03T15:44:22+09:00
# duration_ms = 1462114
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 2
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N, K = map(int, input().split())
S = input()

pre_o = [0] * (N + 1)
for i in range(N):
    pre_o[i + 1] = pre_o[i] + (S[i] == "o")

INF = float("inf")


def check(p: float):
    min_value = INF
    left = 0
    for right in range(1, N + 1):
        while left < right and pre_o[right] - pre_o[left] >= K:
            min_value = min(min_value, pre_o[left] - p * left)
            left += 1

        if min_value <= pre_o[right] - p * right:
            return True

    return False


eps = 1e-10
lo, hi = 0, 1
while hi - lo > eps:
    mid = (lo + hi) / 2
    if check(mid):
        lo = mid
    else:
        hi = mid

print(lo)
