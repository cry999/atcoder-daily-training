import bisect


N = int(input())
C = sorted(list(map(int, input().split())))

# dp[i] := i この品物を買う時の最小費用
dp = [0]*(N+1)
for i, c in enumerate(C):
    dp[i+1] = dp[i] + c

# print(dp)
# O(QxlogN)
for _ in range(int(input())):
    X = int(input())
    n = bisect.bisect_left(dp, X)
    print(n - (n > N or dp[n] != X))
