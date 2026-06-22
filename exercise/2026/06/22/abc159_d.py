N = int(input())
(*A,) = map(int, input().split())

hist = [0] * (N + 1)
for a in A:
    hist[a] += 1

ans = 0
for n in hist:
    ans += n * (n - 1) // 2

for a in A:
    n = hist[a]
    print(ans - n + 1)
