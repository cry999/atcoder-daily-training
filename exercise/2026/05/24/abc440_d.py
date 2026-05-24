from bisect import bisect_left

N, Q = map(int, input().split())
(*A,) = map(int, input().split())
A.sort()

# 許可範囲をソートしてもつ。
ranges = []
if A[0] > 1:
    ranges.append((1, A[0] - 1))
for i in range(N):
    l = A[i] + 1
    if i + 1 < N:
        r = A[i + 1] - 1
    else:
        # 2 * 10^9 が最大
        r = 2 * 10**9

    if l <= r:
        ranges.append((l, r))

M = len(ranges)
# C[i] := i 番目の ranges までの個数の累積和
C = [0] * (M + 1)
for i in range(M):
    l, r = ranges[i]
    C[i + 1] = C[i] + r - l + 1

for _ in range(Q):
    x, y = map(int, input().split())
    start = bisect_left(ranges, x, key=lambda x: x[1])
    l, r = ranges[start]

    l0 = max(x, l)
    r0 = min(l0 + y - 1, r)
    # この範囲の個数は計算不要
    y -= r0 - l0 + 1
    if not y:
        print(r0)
        continue

    lo, hi = start, M + 1
    while hi - lo > 1:
        mi = (lo + hi) // 2
        # NOTE: ranges[start] までの個数は C[start+1] に入っていることに注意。
        c = C[mi] - C[start + 1]
        if c < y:
            lo = mi
        else:
            hi = mi

    l1, _ = ranges[lo]
    c = max(0, C[lo] - C[start + 1])
    ans = l1 + (y - c) - 1
    print(ans)
