N = int(input())
(*A,) = map(int, input().split())

hist = {}

ans = 0
for i in range(N - 1, -1, -1):
    ans += hist.get(i + 1 + A[i], 0)
    hist[i + 1 - A[i]] = hist.get(i + 1 - A[i], 0) + 1

print(ans)
