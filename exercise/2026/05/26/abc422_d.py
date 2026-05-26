N, K = map(int, input().split())

ans = [-1] * (1 << N)


def dfs(total: int, offset: int = 0, remain_step: int = N):
    if remain_step == 0:
        ans[offset] = total
        return

    a = total >> 1
    b = total - a

    remain_step -= 1
    dfs(a, offset, remain_step)
    dfs(b, offset + (1 << remain_step), remain_step)

    return


dfs(K)

print(max(ans) - min(ans))
print(*ans)
