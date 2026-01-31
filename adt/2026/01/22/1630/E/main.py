from collections import defaultdict

N = int(input())
(*A,) = map(int, input().split())

hist = defaultdict(int)
for i, a in enumerate(A):
    hist[a] += 1

ans = -1
for k, v in hist.items():
    if v == 1:
        ans = max(ans, k)
if ans == -1:
    print(ans)
else:
    for i in range(N):
        a = A[i]
        if ans == A[i]:
            print(i + 1)
            break
