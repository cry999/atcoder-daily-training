N, K = map(int, input().split())

if K % (1 << N):
    print(1)
else:
    print(0)

ans = [K // (1 << N)] * (1 << N)
D = K % (1 << N)


def dfs(n: int):
    if n == 1:
        yield 0
        yield 1
        return

    for a in dfs(n - 1):
        yield a
        yield a | (1 << (n - 1))

    return


for i in dfs(N):
    if D == 0:
        break
    D -= 1
    ans[i] += 1

print(*ans)
