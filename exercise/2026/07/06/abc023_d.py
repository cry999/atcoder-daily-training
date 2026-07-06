# >>> atcoder-stat >>>
# started_at  = 2026-07-06T19:22:46+09:00
# solved_at   = 2026-07-06T19:41:27+09:00
# duration_ms = 1121508
# target_ms   = 900000
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 2
# verify      = 3
# <<< atcoder-stat <<<
N = int(input())
baloons = [tuple(map(int, input().split())) for _ in range(N)]

lo, hi = 0, max(h + s * (N - 1) for h, s in baloons)
while hi > lo:
    mid = (hi + lo) // 2
    print(f"[DEBUG] {lo=} {hi=} {mid=}")

    a = [0] * N
    for h, s in baloons:
        print(f"[DEBUG] {min((mid-h)//s, N-1)=}")
        t = min((mid - h) // s, N - 1)
        if t < 0:
            continue
        a[t] += 1

    for t in range(N - 1, -1, -1):
        if a[t] == 0:
            break
        if a[t] > 1:
            a[t - 1] += a[t] - 1
            a[t] = 1

    else:
        hi = mid
        print(f"[DEBUG] {mid=} {a=}")
        continue
    lo = mid + 1

print(hi)
