N, L, W = map(int, input().split())
(*D,) = map(int, input().split())

print(sum(abs(L - d) <= W for d in D))
