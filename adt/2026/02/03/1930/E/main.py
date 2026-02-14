import sys

sys.setrecursionlimit(10**7)


N = int(input())

skill_tree = [[] for _ in range(N)]
skill_time = [0] * N

for i in range(N):
    T, K, *A = map(int, input().split())
    skill_time[i] = T
    skill_tree[i] = [a - 1 for a in A]

acquired = [False] * N


def dfs(n: int) -> int:
    if acquired[n]:
        return 0
    acquired[n] = True

    if not skill_tree[n]:
        return skill_time[n]

    return skill_time[n] + sum(dfs(pre) for pre in skill_tree[n])


print(dfs(N - 1))
