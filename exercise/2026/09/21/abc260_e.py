# >>> atcoder-stat >>>
# started_at  = 2026-09-21T10:44:32+09:00
# solved_at   = 2026-09-21T11:03:16+09:00
# duration_ms = 1124130
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


N, M = map(int, input().split())

indexes = [[] for _ in range(M + 1)]
for i in range(N):
    a, b = map(int, input().split())
    indexes[a].append(i)
    indexes[b].append(i)

# 現在見ている範囲 [l, r) に含まれるペアの数
covered = 0
# 現在見ている範囲 [l, r) に含まれるペア i の要素の数
counts = [0] * N

ans = [0] * (M + 2)

r = 1
for l in range(1, M + 1):
    r = max(r, l)
    while covered < N and r <= M:
        for i in indexes[r]:
            counts[i] += 1
            covered += counts[i] == 1
        r += 1

    print(f"[DEBUG] {l=} {r=}: {covered=}")
    if covered == N:
        print(f"[DEBUG] ==> {r-l=}, {M-l+1=}")
        ans[r - l] += 1
        ans[M - l + 2] -= 1

    for i in indexes[l]:
        counts[i] -= 1
        covered -= counts[i] == 0

for i in range(M + 1):
    ans[i + 1] += ans[i]

print(*ans[1:-1])
