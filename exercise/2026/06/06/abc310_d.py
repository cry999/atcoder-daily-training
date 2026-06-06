N, T, M = map(int, input().split())
hate = [0 for _ in range(N)]

for _ in range(M):
    a, b = map(int, input().split())
    hate[a - 1] |= 1 << (b - 1)
    hate[b - 1] |= 1 << (a - 1)


ans = 0
teams = []


def dfs(i: int):
    global ans

    if i == N:
        ans += len(teams) == T
        return

    for j in range(len(teams)):
        if hate[i] & teams[j]:
            continue

        teams[j] |= 1 << i
        dfs(i + 1)
        teams[j] ^= 1 << i

    if len(teams) < T:
        teams.append(1 << i)
        dfs(i + 1)
        teams.pop()

    return


dfs(0)

print(ans)
