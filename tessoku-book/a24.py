N = int(input())
A = list(map(int, input().split()))

# dp[i]: i 番目まで見たときの最長増加部分列の長さ
dp = [0] * (N)
# L[i]: 長さ i の最長増加部分列の最後の要素の最小値
L = [float('inf')] * (N+1)
L[0] = 0

max_len = 0

for i in range(N):
    # print('---')
    # print(*dp)
    # print(*L)
    # L のなかで A[i] 未満で終わる最長の列を探す
    lo, hi = 0, N
    while lo <= hi:
        mid = (lo + hi) // 2
        if L[mid] < A[i]:
            lo = mid + 1
        else:
            hi = mid - 1

    dp[i] = lo
    L[lo] = min(L[lo], A[i])
    max_len = max(max_len, dp[i])

print(max_len)
