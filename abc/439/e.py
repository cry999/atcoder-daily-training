N = int(input())
kites = [list(map(int, input().split())) for _ in range(N)]
kites.sort(key=lambda x: (x[0], -x[1]))

# dp[i] := Bi が末尾の最長列
dp = [0] * N
# L[i] := i 人が凧を上げた時の最小 Bi
L = [float("inf")] * (N + 1)
L[0] = 0

max_kites = 0
for i in range(N):
    # Yi 未満の高さで最大重の重箱数を二分探索
    lo, hi = 0, N
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if L[mid] < kites[i][1]:
            lo = mid
        else:
            hi = mid - 1

    dp[i] = lo + 1
    L[dp[i]] = min(L[dp[i]], kites[i][1])
    max_boxes = max(max_kites, dp[i])

print(max_kites)
