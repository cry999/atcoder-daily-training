N = int(input())

ans = sum(N / i for i in range(1, N))
print(ans)
