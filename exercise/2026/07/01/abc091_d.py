# >>> atcoder-stat >>>
# started_at  = 2026-07-01T16:20:05+09:00
# solved_at   = 2026-07-01T18:30:54+09:00
# duration_ms = 7849964
# target_ms   = 900000
# ac          = true
# editorial   = true
# knowledge   = 3
# translation = 1
# complexity  = 1
# impl        = 1
# verify      = 1
# <<< atcoder-stat <<<
from bisect import bisect_left

N = int(input())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

BIT = 28

ans = 0
t = 1 << BIT
for _ in range(BIT + 1):
    mask = (2 * t) - 1
    for i in range(N):
        B[i] &= mask
        A[i] &= mask
    A.sort()
    B.sort()

    i1, i2, i3, i4 = 0, 0, 0, 0
    for i in range(N - 1, -1, -1):
        a = A[i]
        # [t, 2t)
        while i1 < N and B[i1] < t - a:
            i1 += 1
        while i2 < N and B[i2] < 2 * t - a:
            i2 += 1

        # [3t, 4t)
        while i3 < N and B[i3] < 3 * t - a:
            i3 += 1
        while i4 < N and B[i4] < 4 * t - a:
            i4 += 1

        cnt = (i2 - i1) + (i4 - i3)

        if cnt % 2:
            ans ^= t

    t >>= 1
    print(f"[DEBUG] {ans=}")
print(ans)
