N = int(input())

A = tuple(sorted(map(int, input().split())))
ans = set()


def xor(a: list[int]):
    ret = 0
    for x in a:
        ret ^= x
    return ret


groups = [0] * N


def dfs(d: int, k: int = 0):
    if d == N:
        ans.add(xor(groups))
        return

    for i in range(k):
        groups[i] += A[d]
        dfs(d + 1, k)
        groups[i] -= A[d]

    groups[k] += A[d]
    dfs(d + 1, k + 1)
    groups[k] -= A[d]
    return


dfs(0)

print(len(ans))
