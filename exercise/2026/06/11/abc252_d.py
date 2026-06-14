from collections import defaultdict

N = int(input())
(*A,) = map(int, input().split())

hist = defaultdict(int)
for a in A:
    hist[a] += 1

ans = N * (N - 1) * (N - 2) // 6
for a in hist.keys():
    n = hist[a]
    # 同じ数 x2 + 異なる数 x1
    ans -= (N - n) * n * (n - 1) // 2
    # 同じ数 x3
    ans -= n * (n - 1) * (n - 2) // 6
print(ans)
