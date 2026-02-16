N, K = map(int, input().split())
(*A,) = map(int, input().split())

for i, a in enumerate(A):
    if a == K:
        print(i + 1)
        break
else:
    print(-1)
