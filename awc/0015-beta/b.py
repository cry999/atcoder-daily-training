N, K = map(int, input().split())
(*P,) = map(int, input().split())

ans = -1
for i, p in enumerate(P):
    if p >= K:
        ans = i + 1
        break
print(ans)
