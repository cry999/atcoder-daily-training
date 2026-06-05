N, M = map(int, input().split())

ans = []
a = []


def dfs(i: int):
    if i == 0:
        ans.append(a[:])
        return

    x = 1
    if a:
        x = a[-1] + 10

    for y in range(x, M - 10 * (i - 1) + 1):
        # print(f"{i=}, {y=}")
        a.append(y)
        dfs(i - 1)
        a.pop()

    return


dfs(N)

print(len(ans))
for x in ans:
    print(*x)
