N = int(input())
(*A,) = map(int, input().split())

hist = {}
for a in A:
    hist[a] = hist.get(a, 0) + 1

ans_n = -1
for k, v in hist.items():
    if v > 1:
        continue
    ans_n = max(ans_n, k)

ans = -1
for i, a in enumerate(A):
    if a == ans_n:
        ans = i + 1
print(ans)
