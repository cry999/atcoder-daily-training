N, K = map(int, input().split())
(*D,) = map(int, input().split())

D.sort()
print(sum(D[: N - K]))
